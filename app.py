import json
import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

import plotly
import plotly.graph_objects as go
from flask import Flask, Response, jsonify, render_template, request, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from bi_metrics import BI_METRICS, action_label, exit_reason_label, position_label, score_metric
from bi_report import render_markdown
from bi_suite import (
    ALGORITHMS,
    _load_algorithm,
    load_algorithm_catalog,
    load_bi_results,
    refresh_bi_results_if_allowed,
)
from benchmarks import dollar_benchmark, ibovespa_benchmark
from cms import about_page_context, context_path, read_context_raw
from simulator import run_backtest
from validation import validate_simulation_form

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

if os.environ.get("TRUSTED_PROXY", "1") == "1":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.jinja_env.globals["bi_metrics"] = BI_METRICS
app.jinja_env.globals["bi_score"] = score_metric
app.jinja_env.globals["position_label"] = position_label
app.jinja_env.globals["action_label"] = action_label
app.jinja_env.globals["exit_reason_label"] = exit_reason_label


def get_client_ip():
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return get_remote_address()


limiter = Limiter(
    get_client_ip,
    app=app,
    default_limits=["1 per second"],
    storage_uri="memory://",
)


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.errorhandler(429)
def ratelimit_handler(exc):
    if request.path == "/" and request.method == "POST":
        message = "Simulation rate limit: one run per minute."
    else:
        message = "Too many requests. Please wait a moment."
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"error": message}), 429
    return render_template("error.html", message=message), 429


def _avg_metric(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else 0.0


def _encode_fig(fig):
    return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


def _build_bi_charts(results, market_benchmark, dollar_benchmark_data, summary, algorithm_catalog):
    ok_results = [r for r in results if r["status"] == "ok"]
    algo_names = [a["name"] for a in algorithm_catalog]

    by_algo = defaultdict(list)
    for row in ok_results:
        by_algo[row["algorithm"]].append(row)

    strategy_avgs = [_avg_metric(by_algo[a], "return_pct") for a in algo_names]
    buy_hold_avgs = [_avg_metric(by_algo[a], "buy_hold_return_pct") for a in algo_names]
    ibov_line = [summary["ibovespa_return_pct"]] * len(algo_names)
    dollar_line = [summary["dollar_return_pct"]] * len(algo_names)

    scatter_fig = go.Figure()
    for algo in algorithm_catalog:
        perf = algo.get("performance") or {}
        if not perf:
            continue
        scatter_fig.add_trace(
            go.Scatter(
                x=[perf.get("avg_max_drawdown_pct", 0)],
                y=[perf.get("avg_return_pct", 0)],
                mode="markers+text",
                name=algo["name"],
                text=[algo["name"]],
                textposition="top center",
                marker=dict(size=12),
            )
        )
    scatter_fig.add_trace(
        go.Scatter(
            x=[summary.get("avg_buy_hold_max_drawdown_pct", 0)],
            y=[summary.get("avg_buy_hold_pct", 0)],
            mode="markers+text",
            name="Comprar e manter (média)",
            text=["Comprar e manter"],
            textposition="bottom center",
            marker=dict(size=14, symbol="diamond", color="#fd7e14"),
        )
    )
    scatter_fig.update_layout(
        title="Risco vs retorno — menor drawdown e maior retorno é melhor",
        xaxis_title="Drawdown máximo (%)",
        yaxis_title="Retorno médio (%)",
        height=420,
        margin=dict(t=60, b=60),
        shapes=[
            dict(type="rect", xref="paper", yref="paper", x0=0, x1=0.5, y0=0.5, y1=1,
                 fillcolor="rgba(13,110,253,0.04)", line_width=0),
            dict(type="rect", xref="paper", yref="paper", x0=0.5, x1=1, y0=0, y1=0.5,
                 fillcolor="rgba(253,126,20,0.04)", line_width=0),
        ],
        annotations=[
            dict(x=0.12, y=0.95, xref="paper", yref="paper", text="Alpha genuíno", showarrow=False,
                 font=dict(size=11, color="#6c757d")),
            dict(x=0.72, y=0.95, xref="paper", yref="paper", text="Redução de risco", showarrow=False,
                 font=dict(size=11, color="#6c757d")),
            dict(x=0.72, y=0.08, xref="paper", yref="paper", text="Defensivo", showarrow=False,
                 font=dict(size=11, color="#6c757d")),
            dict(x=0.12, y=0.08, xref="paper", yref="paper", text="Subdesempenho", showarrow=False,
                 font=dict(size=11, color="#6c757d")),
        ],
    )

    risk_scores = summary.get("risk_scores") or {}
    score_names = sorted(risk_scores, key=risk_scores.get, reverse=True)
    risk_score_fig = go.Figure(
        data=[
            go.Bar(
                x=score_names,
                y=[risk_scores[n] for n in score_names],
                marker_color="#0d6efd",
                text=[f"{risk_scores[n]:.0f}" for n in score_names],
                textposition="outside",
            )
        ]
    )
    risk_score_fig.update_layout(
        title="Score de redução de risco (maior = melhor perfil ajustado ao risco)",
        yaxis_title="Score (0–100)",
        height=340,
        margin=dict(t=60, b=60),
    )

    drawdown_fig = go.Figure()
    best_algo = summary.get("best_risk_score_algo")
    showcase = None
    if best_algo and by_algo.get(best_algo):
        showcase = max(by_algo[best_algo], key=lambda r: r.get("protection_alpha_pp", 0))
    if showcase and showcase.get("drawdown_series"):
        s_dates = [p["date"] for p in showcase["drawdown_series"]]
        s_dd = [p["drawdown_pct"] for p in showcase["drawdown_series"]]
        b_dd = [p["drawdown_pct"] for p in showcase.get("buy_hold_drawdown_series", [])]
        drawdown_fig.add_trace(
            go.Scatter(x=s_dates, y=s_dd, mode="lines", name=f"{best_algo}", line=dict(color="#0d6efd", width=2))
        )
        drawdown_fig.add_trace(
            go.Scatter(x=s_dates, y=b_dd[: len(s_dates)], mode="lines", name="Comprar e manter", line=dict(color="#fd7e14", width=2, dash="dash"))
        )
        peak_s = min(s_dd) if s_dd else 0
        peak_b = min(b_dd) if b_dd else 0
        drawdown_fig.update_layout(
            title=(
                f"Curva de drawdown — {best_algo} · {showcase['symbol']} "
                f"(pico {peak_s:.1f}% vs {peak_b:.1f}% comprar e manter)"
            ),
            yaxis_title="Drawdown (%)",
            height=360,
            margin=dict(t=60, b=60),
        )
    else:
        drawdown_fig.update_layout(title="Curva de drawdown (sem dados)", height=200)

    rolling_fig = go.Figure()
    for algo in algorithm_catalog[:3]:
        rows = by_algo.get(algo["name"], [])
        if not rows:
            continue
        sample = rows[0]
        roll = (sample.get("rolling") or {}).get("90", {}).get("sharpe", [])
        if roll:
            rolling_fig.add_trace(
                go.Scatter(
                    x=[p["date"] for p in roll],
                    y=[p["value"] for p in roll],
                    mode="lines",
                    name=algo["name"],
                )
            )
    rolling_fig.update_layout(
        title="Sharpe móvel 90 pregões (amostra — verificação de consistência)",
        yaxis_title="Sharpe",
        height=360,
        margin=dict(t=60, b=60),
    )

    comparison_fig = go.Figure()
    comparison_fig.add_trace(go.Bar(name="Estratégia", x=algo_names, y=strategy_avgs, text=[f"{v:.2f}%" for v in strategy_avgs], textposition="outside"))
    comparison_fig.add_trace(go.Bar(name="Comprar e manter", x=algo_names, y=buy_hold_avgs, text=[f"{v:.2f}%" for v in buy_hold_avgs], textposition="outside"))
    comparison_fig.add_trace(go.Scatter(name="Ibovespa", x=algo_names, y=ibov_line, mode="lines+markers", line=dict(color="#6f42c1", width=2)))
    comparison_fig.add_trace(go.Scatter(name="USD/BRL", x=algo_names, y=dollar_line, mode="lines+markers", line=dict(color="#20c997", width=2, dash="dash")))
    comparison_fig.update_layout(
        title="Comparação de retorno bruto (secundário — ver métricas de risco acima)",
        yaxis_title="Return (%)",
        barmode="group",
        height=380,
        margin=dict(t=60, b=80),
    )

    ibov_fig = go.Figure()
    if market_benchmark.get("normalized_series"):
        dates = [point["date"] for point in market_benchmark["normalized_series"]]
        values = [point["index"] for point in market_benchmark["normalized_series"]]
        ibov_fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name="Ibovespa (indexed)", line=dict(color="#6f42c1", width=2)))
    ibov_fig.update_layout(
        title=f"Ibovespa em {market_benchmark.get('period', '')} / {market_benchmark.get('interval', '')} (início = 100)",
        yaxis_title="Nível indexado",
        height=360,
        margin=dict(t=60, b=60),
    )

    dollar_fig = go.Figure()
    if dollar_benchmark_data.get("normalized_series"):
        dates = [point["date"] for point in dollar_benchmark_data["normalized_series"]]
        values = [point["index"] for point in dollar_benchmark_data["normalized_series"]]
        dollar_fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name="USD/BRL (indexed)", line=dict(color="#20c997", width=2)))
    dollar_fig.update_layout(
        title=f"USD/BRL em {dollar_benchmark_data.get('period', '')} / {dollar_benchmark_data.get('interval', '')} (início = 100)",
        yaxis_title="BRL por USD indexado",
        height=360,
        margin=dict(t=60, b=60),
    )

    benchmark_fig = go.Figure(
        data=[
            go.Bar(
                x=["Estratégias (média)", "Comprar e manter (média)", "Ibovespa", "USD/BRL"],
                y=[
                    summary["avg_return_pct"],
                    summary["avg_buy_hold_pct"],
                    summary["ibovespa_return_pct"],
                    summary["dollar_return_pct"],
                ],
                marker_color=["#0d6efd", "#fd7e14", "#6f42c1", "#20c997"],
                text=[
                    f"{summary['avg_return_pct']:.2f}%",
                    f"{summary['avg_buy_hold_pct']:.2f}%",
                    f"{summary['ibovespa_return_pct']:.2f}%",
                    f"{summary['dollar_return_pct']:.2f}%",
                ],
                textposition="outside",
            )
        ]
    )
    benchmark_fig.update_layout(
        title="Contexto de mercado — o período amostral foi enviesado?",
        yaxis_title="Return (%)",
        height=340,
        margin=dict(t=60, b=60),
    )

    per_test_drawdown = {}
    for row in ok_results:
        if row.get("drawdown_series"):
            per_test_drawdown[str(row["test_id"])] = {
                "strategy": row["drawdown_series"],
                "buy_hold": row.get("buy_hold_drawdown_series", []),
                "title": f"{row['algorithm']} · {row['symbol']}",
            }

    return json.dumps(
        {
            "risk_scatter": _encode_fig(scatter_fig),
            "risk_score": _encode_fig(risk_score_fig),
            "drawdown": _encode_fig(drawdown_fig),
            "rolling": _encode_fig(rolling_fig),
            "comparison": _encode_fig(comparison_fig),
            "ibovespa": _encode_fig(ibov_fig),
            "dollar": _encode_fig(dollar_fig),
            "benchmark": _encode_fig(benchmark_fig),
            "per_test_drawdown": per_test_drawdown,
        }
    )


def _bi_page_context(data, refresh_meta=None):
    context = {
        "generated_at": data["generated_at"],
        "market": data.get("market", "B3 (Bovespa)"),
        "scenario": data["scenario"],
        "test_count": data["test_count"],
        "algorithm_count": data["algorithm_count"],
        "stock_count": data.get("stock_count", 10),
        "period": data.get("period", "1y"),
        "interval": data.get("interval", "1d"),
        "market_benchmark": data.get("market_benchmark", {}),
        "dollar_benchmark": data.get("dollar_benchmark", {}),
        "summary": data["summary"],
        "results": data["results"],
        "algorithm_catalog": load_algorithm_catalog(data["results"]),
        "chart_data": _build_bi_charts(
            data["results"],
            data.get("market_benchmark", {}),
            data.get("dollar_benchmark", {}),
            data["summary"],
            load_algorithm_catalog(data["results"]),
        ),
        "expanded": False,
        "export_mode": False,
        "refresh_blocked": False,
        "next_refresh_at": None,
        "refresh_message": None,
    }
    if refresh_meta:
        context.update(refresh_meta)
    return context


@app.route("/health")
@limiter.exempt
def health():
    return jsonify({"status": "ok"})


@app.route("/about")
def about():
    bi = load_bi_results()
    return render_template("about.html", **about_page_context(bi))


@app.route("/content/context.md")
def cms_context_source():
    return Response(
        read_context_raw(),
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{context_path().name}"'},
    )


@app.route("/bi")
def bi_dashboard():
    force_refresh = bool(request.args.get("refresh"))
    data, refresh_meta = refresh_bi_results_if_allowed(get_client_ip(), force_refresh=force_refresh)
    if force_refresh and refresh_meta.get("refresh_blocked"):
        logger.info("BI refresh blocked for %s until %s", get_client_ip(), refresh_meta.get("next_refresh_at"))
    return render_template("bi.html", **_bi_page_context(data, refresh_meta))


@app.route("/bi/export/html")
def bi_export_html():
    data = load_bi_results()
    static_dir = Path(app.root_path) / "static"
    context = _bi_page_context(data)
    context["expanded"] = True
    context["export_mode"] = True
    context["inline_bootstrap_css"] = (static_dir / "vendor" / "bootstrap.min.css").read_text(encoding="utf-8")
    context["inline_css"] = (static_dir / "styles.css").read_text(encoding="utf-8")
    context["bi_page_js"] = (static_dir / "bi_page.js").read_text(encoding="utf-8")
    html = render_template("bi_export.html", **context)
    return Response(
        html,
        mimetype="text/html; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bi_benchmark.html"},
    )


@app.route("/bi/export/markdown")
def bi_export_markdown():
    data = load_bi_results()
    catalog = load_algorithm_catalog(data["results"])
    markdown = render_markdown(data, algorithm_catalog=catalog)
    return Response(
        markdown,
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bi_benchmark.md"},
    )


@app.route("/bi/report")
def bi_report():
    report_path = Path("static/bi_report.md")
    if request.args.get("refresh"):
        _, refresh_meta = refresh_bi_results_if_allowed(get_client_ip(), force_refresh=True)
        if refresh_meta.get("refresh_blocked"):
            logger.info("BI report refresh blocked for %s", get_client_ip())
    elif not report_path.exists():
        load_bi_results()
    return send_file(report_path, mimetype="text/markdown; charset=utf-8")


@app.route("/", methods=["GET", "POST"])
@limiter.limit("1 per minute", methods=["POST"])
def index():
    if request.method == "GET":
        return render_template(
            "index.html",
            algorithms=sorted(ALGORITHMS.keys()),
        )

    try:
        params = validate_simulation_form(request.form)
        algorithm_source = _load_algorithm(ALGORITHMS[params["algorithm"]])

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                run_backtest,
                symbol=params["symbol"],
                period=params["period"],
                interval=params["interval"],
                algorithm_source=algorithm_source,
                initial_balance=params["initial_balance"],
                lot_size_pct=params["lot_size_pct"],
                commission_pct=params["commission_pct"],
                initial_stocks=params["initial_stocks"],
                include_graph=True,
            )
            result = future.result(timeout=90)

        ibov = ibovespa_benchmark(params["period"], params["interval"], params["initial_balance"])
        dollar = dollar_benchmark(params["period"], params["interval"], params["initial_balance"])
        vs_ibovespa = result["return_pct"] - ibov["buy_hold_return_pct"]
        vs_dollar = result["return_pct"] - dollar["buy_hold_return_pct"]

        output = result["output"]
        output.append(
            {
                "Action": "Summary",
                "Message": (
                    f"Ibovespa: {ibov['buy_hold_return_pct']:.2f}% · "
                    f"Strategy vs Ibovespa: {vs_ibovespa:+.2f} pp"
                ),
            }
        )
        output.append(
            {
                "Action": "Summary",
                "Message": (
                    f"USD/BRL: {dollar['buy_hold_return_pct']:.2f}% · "
                    f"Strategy vs dollar: {vs_dollar:+.2f} pp"
                ),
            }
        )

        graph = json.dumps(result["graph"]) if result.get("graph") else "{}"
        gain_amount = result["gain_amount"]
        return_pct = result["return_pct"]
        vs_buy_hold = result["vs_buy_hold_pct"]

        return render_template(
            "backtest.html",
            output=output,
            graph=graph,
            symbol=result["symbol"],
            period=params["period"],
            interval=params["interval"],
            initial_balance=f"{params['initial_balance']:,.2f}",
            total_value=f"{result['total_value']:,.2f}",
            gain_amount=f"{gain_amount:,.2f}",
            return_pct=f"{return_pct:.2f}",
            gain_positive=gain_amount >= 0,
            final_position=result["final_position"],
            final_shares=result["final_shares"],
            buy_hold_return_pct=f"{result['buy_hold_return_pct']:.2f}",
            vs_buy_hold_pct=f"{vs_buy_hold:+.2f}",
            ibovespa_return_pct=f"{ibov['buy_hold_return_pct']:.2f}",
            vs_ibovespa_pct=f"{vs_ibovespa:+.2f}",
            dollar_return_pct=f"{dollar['buy_hold_return_pct']:.2f}",
            vs_dollar_pct=f"{vs_dollar:+.2f}",
            name=result["name"],
            algorithm_name=params["algorithm"],
        )

    except FuturesTimeoutError:
        return render_template("error.html", message="Simulation timed out after 90 seconds."), 504
    except Exception as exc:
        logger.exception("Simulation failed")
        return render_template("error.html", message=str(exc)), 400
