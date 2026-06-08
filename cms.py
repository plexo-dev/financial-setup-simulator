"""File-based CMS: content/context.md is the single source of truth for site copy."""

import re
from pathlib import Path

_SECTION_ORDER = [
    ("product", 1),
    ("business", 2),
    ("architecture", 3),
    ("compliance", 4),
]

_HEADING_RE = re.compile(r"^[^\d]*(\d+)\.\s+(.+?)\s*$")
_TIER_RE = re.compile(
    r"^Plano\s+(\w+)\s+\(R\$\s*(\d+)/m[eê]s\):\s*(.+)$",
    re.IGNORECASE,
)

_DEFAULT_CONTEXT_PATHS = (Path("content/context.md"),)

_FALLBACK_PRICING = [
    {
        "name": "Starter",
        "price": 29,
        "currency": "R$",
        "period": "mês",
        "description": "Recursos limitados e taxa de comissão maior sobre simulações ou relatórios exportados.",
        "featured": False,
    },
    {
        "name": "Pro",
        "price": 99,
        "currency": "R$",
        "period": "mês",
        "description": "Plano de equilíbrio, desenhado como a principal ferramenta de retenção e conveniência.",
        "featured": True,
    },
    {
        "name": "Premium",
        "price": 199,
        "currency": "R$",
        "period": "mês",
        "description": "Funcionalidades ilimitadas e livre de taxas adicionais.",
        "featured": False,
    },
]


def context_path():
    for path in _DEFAULT_CONTEXT_PATHS:
        if path.is_file():
            return path
    return _DEFAULT_CONTEXT_PATHS[-1]


def read_context_raw(path=None):
    return (path or context_path()).read_text(encoding="utf-8")


def _strip_emoji(text):
    return re.sub(
        r"^[\U0001F300-\U0001FAFF\u2600-\u27BF]+\s*",
        "",
        text.strip(),
    ).strip()


def _paragraphs_from_body(body):
    paragraphs = []
    current = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if stripped.startswith("-") or stripped.startswith("•"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(_strip_emoji(stripped.lstrip("-•").strip()))
        else:
            current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))
    return [p for p in paragraphs if p]


def parse_context_md(path=None):
    text = read_context_raw(path)
    sections = {}
    current_key = None
    current_title = None
    current_lines = []

    for line in text.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            if current_key is not None:
                body = "\n".join(current_lines).strip()
                sections[current_key] = {
                    "title": current_title,
                    "body": _paragraphs_from_body(body),
                }
            section_num = int(match.group(1))
            key = next((k for k, n in _SECTION_ORDER if n == section_num), None)
            if key is None:
                current_key = None
                continue
            current_key = key
            current_title = _strip_emoji(match.group(2))
            current_lines = []
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        body = "\n".join(current_lines).strip()
        sections[current_key] = {
            "title": current_title,
            "body": _paragraphs_from_body(body),
        }

    return sections


def pricing_tiers(sections=None):
    sections = sections or parse_context_md()
    tiers = []
    for paragraph in sections.get("business", {}).get("body", []):
        match = _TIER_RE.match(paragraph)
        if not match:
            continue
        name = match.group(1)
        tiers.append(
            {
                "name": name,
                "price": int(match.group(2)),
                "currency": "R$",
                "period": "mês",
                "description": match.group(3).strip(),
                "featured": name.lower() == "pro",
            }
        )
    return tiers or list(_FALLBACK_PRICING)


def business_intro(sections=None):
    sections = sections or parse_context_md()
    intro = []
    for paragraph in sections.get("business", {}).get("body", []):
        if _TIER_RE.match(paragraph):
            break
        if paragraph in {"Processamento Financeiro", "Estrutura de Planos (Pricing Tiers)"}:
            continue
        if paragraph.startswith("Gateway:") or paragraph.startswith("Método:") or paragraph.startswith("Fiscal:"):
            break
        intro.append(paragraph)
    return intro


def regulatory_disclaimer(sections=None):
    sections = sections or parse_context_md()
    paragraphs = sections.get("compliance", {}).get("body", [])
    start = 0
    for idx, paragraph in enumerate(paragraphs):
        if "blindagem jurídica" in paragraph.lower() or "cvm" in paragraph.lower():
            start = idx + 1 if "blindagem jurídica" in paragraph.lower() else idx
            break
    return [p for p in paragraphs[start:] if p and not p.startswith("Sandbox")]


def build_about_pitch(bi_data):
    summary = bi_data.get("summary") or {}
    risk_scores = summary.get("risk_scores") or {}
    top_risk_scores = sorted(risk_scores.items(), key=lambda item: item[1], reverse=True)[:3]

    return {
        "scenario": bi_data.get("scenario", ""),
        "test_count": bi_data.get("test_count", 0),
        "algorithm_count": bi_data.get("algorithm_count", 0),
        "stock_count": bi_data.get("stock_count", 0),
        "period": bi_data.get("period", ""),
        "generated_at": bi_data.get("generated_at", ""),
        "avg_max_drawdown_pct": summary.get("avg_max_drawdown_pct"),
        "avg_buy_hold_max_drawdown_pct": summary.get("avg_buy_hold_max_drawdown_pct"),
        "avg_exposure_pct": summary.get("avg_exposure_pct"),
        "avg_sharpe": summary.get("avg_sharpe"),
        "best_risk_score_algo": summary.get("best_risk_score_algo"),
        "best_risk_score": summary.get("best_risk_score"),
        "risk_scores_top": top_risk_scores,
        "protection_alpha_pp": summary.get("protection_alpha_pp"),
    }


def about_page_context(bi_data):
    sections = parse_context_md()
    return {
        "sections": sections,
        "pitch": build_about_pitch(bi_data),
        "pricing": pricing_tiers(sections),
        "business_intro": business_intro(sections),
        "disclaimer": regulatory_disclaimer(sections),
    }
