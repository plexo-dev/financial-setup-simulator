# Benchmark de estratégias B3 ajustado ao risco

**Gerado em:** 2026-06-08 00:19 UTC  
**Mercado:** B3 (Bovespa)  
**Cenário:** B3 · 5 algoritmos × 10 papéis · 1y / 1d · saldo inicial R$ 10,000  
**Período:** 1y / 1d  

> Simulação histórica — não é trading ao vivo. Sharpe usa taxa livre de risco 0%. Valor de proteção é um composto narrativo, não alpha de Jensen.

## Resumo executivo

As estratégias retornaram 2.2% vs 2.2% comprar e manter, reduzindo o drawdown máximo de 25.8% para 3.9%. O tempo médio no mercado é de apenas 11%, com 9% de captura de alta e 7% de captura de baixa — a redução de risco acompanha menor exposição, não participação seletiva.


As estratégias não demonstram geração relevante de alpha versus comprar e manter, mas alcançam redução substancial de drawdown e volatilidade. Com apenas 11% de tempo médio no mercado e 9% de captura de alta, a maior parte da redução de risco parece vir de menor exposição ao mercado, e não de seleção de papéis ou timing superiores. Pesquisas futuras devem focar em aumentar a captura de alta (meta 50–70%) preservando a proteção na baixa (meta 20–40%).


## Eficiência de risco

_↑ Retorno, Sharpe, captura de alta · ↓ Volatilidade, drawdown máx., captura de baixa (seletiva), runs sem trades_

| Métrica | Estratégia (média) | Comprar e manter (média) |
| --- | ---: | ---: |
| Retorno | 2.16% | 2.18% |
| Volatilidade (an.) | 5.7% | 32.6% |
| Drawdown máximo | 3.9% | 25.8% |
| Sharpe | 0.23 | 0.28 |
| Captura de baixa | 7% | 100% (ref) |
| Captura de alta | 9% | 100% (ref) |
| Tempo no mercado | 11% | 100% (ref) |

## Análise de exposição

_Baixa exposição = muito em caixa. ↑ Captura de alta · ↓ Captura de baixa (seletiva), runs sem trades_

| Estratégia | Tempo no mercado | Média de trades | Runs sem trades | Capt. alta | Capt. baixa |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20-day breakout | 4.5% | 2.4 | 2 / 10 | 5% | 2% |
| RSI reversion | 1.9% | 1.8 | 1 / 10 | 2% | 1% |
| SMA-20 trend | 7.8% | 1.8 | 5 / 10 | 6% | 5% |
| SMA crossover | 11.2% | 2.4 | 3 / 10 | 9% | 8% |
| SMA-8 trend | 29.2% | 7.6 | 0 / 10 | 21% | 21% |

## Sinal vs motor de risco (A/B/C)

_↑ Retorno, captura de alta · ↓ DD máx. · Δ retorno vs A: sinalado_

### SMA-8 trend

| Versão | Retorno | DD máx. | Exposição | Capt. alta | Δ retorno vs A |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · Só sinal | 7.12% | 11.3% | 46.5% | 34.62 | +0.00 pp |
| B · Sinal + saídas de risco | 5.46% | 12.1% | 44.5% | 33.11 | -1.66 pp |
| C · Estratégia completa | 2.48% | 9.0% | 29.2% | 20.95 | -4.64 pp |

### SMA-20 trend

| Versão | Retorno | DD máx. | Exposição | Capt. alta | Δ retorno vs A |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · Só sinal | 2.57% | 14.1% | 43.9% | 31.77 | +0.00 pp |
| B · Sinal + saídas de risco | 1.31% | 12.5% | 36.8% | 26.35 | -1.26 pp |
| C · Estratégia completa | 2.06% | 3.0% | 7.8% | 6.38 | -0.51 pp |

### SMA crossover

| Versão | Retorno | DD máx. | Exposição | Capt. alta | Δ retorno vs A |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · Só sinal | 4.42% | 6.4% | 19.5% | 14.61 | +0.00 pp |
| B · Sinal + saídas de risco | 2.48% | 5.4% | 11.9% | 9.02 | -1.94 pp |
| C · Estratégia completa | 2.88% | 4.9% | 11.2% | 8.65 | -1.55 pp |

### RSI reversion

| Versão | Retorno | DD máx. | Exposição | Capt. alta | Δ retorno vs A |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · Só sinal | -0.04% | 10.7% | 27.6% | 20.09 | +0.00 pp |
| B · Sinal + saídas de risco | -1.80% | 4.9% | 4.5% | 3.21 | -1.75 pp |
| C · Estratégia completa | 1.16% | 1.1% | 1.9% | 1.73 | +1.21 pp |

### 20-day breakout

| Versão | Retorno | DD máx. | Exposição | Capt. alta | Δ retorno vs A |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · Só sinal | -1.06% | 5.9% | 10.8% | 7.69 | +0.00 pp |
| B · Sinal + saídas de risco | -1.06% | 5.9% | 10.8% | 7.69 | -0.00 pp |
| C · Estratégia completa | 2.20% | 1.8% | 4.5% | 5.08 | +3.26 pp |


### Score de redução de risco

_↑ Score maior é melhor_

| Estratégia | Score |
| --- | ---: |
| 20-day breakout | 92 |
| RSI reversion | 69 |
| SMA-20 trend | 60 |
| SMA crossover | 38 |
| SMA-8 trend | 4 |

## Contexto de mercado

_↑ Retorno do benchmark · Superar comprar e manter: contagem maior é melhor_

| Benchmark | Retorno |
| --- | ---: |
| Estratégias (média) | 2.16% |
| Comprar e manter (média) | 2.18% |
| Ibovespa (^BVSP) | 24.06% |
| USD/BRL (USDBRL=X) | -7.40% |

## Resumo (secundário)

- **Testes:** 50 (5 algoritmos × 10 papéis)
- **Superou comprar e manter:** 27 / 50
- **Média vs comprar e manter:** -0.02 pp

## Algoritmos

### 20-day breakout (Donchian channel breakout)

Turtle-style breakout: close above the prior 20-day high after a volatility squeeze. BB width percentile filter avoids late, expensive breakouts common on B3.

- **Indicadores:** 20-day high/low (prior bar), SMA-50, BB width + 70th percentile, ATR(14), 22-day high, volume.
- **Lógica de compra:** Close above yesterday’s 20-day high; price above SMA-50; BB width below its 100-bar 70th percentile (squeeze); volume confirmation; cooldown near last sell.
- **Lógica de venda:** ATR stop-loss (2.5× ATR), chandelier trail, break below 20-day low, or two consecutive closes below breakout level (fakeout exit).

#### Performance ajustada ao risco

| Métrica | Valor |
| --- | ---: |
| Score de risco | 92 |
| Retorno médio | 2.20% |
| C&M médio | 2.18% |
| Sharpe | 0.87 (C&M -0.33) |
| Drawdown máximo | 1.8% (C&M 25.0%) |
| Captura de baixa | 2.08 |
| Tempo no mercado | 4.5% |
| Runs sem trades | 2 / 10 |
| Superou C&M | 5 / 10 |

#### Performance por regime

| Alta | Baixa | Lateral | Alta vol. |
| --- | ---: | ---: | ---: |
| 39.2% | 0.0% | 8.2% | -1.4% |

#### Atribuição de saídas

| Razão | PnL médio % |
| --- | ---: |
| Saída falso rompimento | +2.20% |

Motor de sinal: +2.20% · Motor de risco: +0.00%

#### Resultados por papel

| Papel | Retorno | Sharpe | DD máx. | vs C&M | Trades |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 1.72% | 0.92 | 2.1% | -20.21 pp | 4 |
| BBAS3.SA | 8.58% | 2.83 | 1.6% | +20.35 pp | 2 |
| BBDC4.SA | 5.33% | 2.24 | 2.2% | -13.59 pp | 4 |
| CYRE3.SA | 0.00% | 0.00 | 0.0% | +15.65 pp | 0 |
| ITUB4.SA | 4.85% | 1.91 | 3.2% | -14.83 pp | 4 |
| LREN3.SA | 0.63% | 0.33 | 2.2% | +15.18 pp | 4 |
| RADL3.SA | -1.97% | -0.81 | 3.1% | -23.44 pp | 2 |
| RENT3.SA | 0.32% | 0.20 | 1.6% | +3.90 pp | 2 |
| SUZB3.SA | 0.00% | 0.00 | 0.0% | +19.36 pp | 0 |
| WEGE3.SA | 2.51% | 1.12 | 1.6% | -2.15 pp | 2 |


#### Código-fonte (`algorithms/breakout_20d.py`)

```python
import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["high20"] = df["High"].rolling(window=20).max().shift(1)
    df["low20"] = df["Low"].rolling(window=20).min().shift(1)
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_width"] = (df["std20"] * 4) / df["sma50"]
    df["bb_width_p70"] = df["bb_width"].rolling(100).quantile(0.7)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    if "Volume" in df.columns:
        df["vol_avg20"] = df["Volume"].rolling(window=20).mean()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    trail = df["high22"].iloc[-1] - 2.5 * atr
    fakeout = len(df) >= 2 and price < df["high20"].iloc[-1] and df["Close"].iloc[-2] < df["high20"].iloc[-2]
    reason = first_sell_reason([
        ("ATR stop", price < entry - 25.0 * atr),
        ("Chandelier trail", price < trail),
        ("Break below 20d low", price < df["low20"].iloc[-1]),
        ("Fakeout exit", fakeout),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    high20 = df["high20"].iloc[-1]
    if price <= high20 * 1.002:
        return entry_gate(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        if df["bb_width"].iloc[-1] > df["bb_width_p70"].iloc[-1]:
            return entry_gate(False, portfolio)
        y = portfolio.get("_entry_reluctance", 1.0)
        vol_mult = 1.1 + max(0.0, y - 1.0) * 0.1
        if "vol_avg20" in df.columns and df["Volume"].iloc[-1] < df["vol_avg20"].iloc[-1] * vol_mult:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf") and sold * 0.97 < price < sold * 1.04:
            return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
```

### RSI reversion (Mean reversion in an uptrend)

Buys short-term pullbacks in stocks that are still in a longer uptrend. RSI and SMA-50 set context; TA-Lib candlestick patterns confirm timing unless RSI is deeply oversold.

- **Indicadores:** RSI(14), SMA-21, SMA-50 and its slope, TA-Lib CDL bullish reversal composite, Bollinger upper (20, 2), Wilder ATR(14), 22-day high.
- **Lógica de compra:** RSI below a dynamic threshold (~40, tighter late-window); price above rising SMA-50; TA-Lib bullish reversal on current or prior bar unless RSI < 32; no chase above last sell (+3%); cooldown near last sell.
- **Lógica de venda:** Adaptive ATR stop (2× below SMA-21, else 2.5×), take profit at upper Bollinger when RSI > 62 (or RSI > 72), or chandelier trail on 22-day high.

#### Performance ajustada ao risco

| Métrica | Valor |
| --- | ---: |
| Score de risco | 69 |
| Retorno médio | 1.16% |
| C&M médio | 2.18% |
| Sharpe | -0.04 (C&M 0.48) |
| Drawdown máximo | 1.1% (C&M 26.0%) |
| Captura de baixa | 1.05 |
| Tempo no mercado | 1.9% |
| Runs sem trades | 1 / 10 |
| Superou C&M | 5 / 10 |

#### Performance por regime

| Alta | Baixa | Lateral | Alta vol. |
| --- | ---: | ---: | ---: |
| 3.2% | 0.0% | -1.9% | 0.2% |

#### Atribuição de saídas

| Razão | PnL médio % |
| --- | ---: |
| Take profit Bollinger | +0.85% |
| RSI sobrecomprado | +0.50% |
| Trailing chandelier | -0.19% |

Motor de sinal: +1.35% · Motor de risco: -0.19%

#### Resultados por papel

| Papel | Retorno | Sharpe | DD máx. | vs C&M | Trades |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 0.13% | 0.12 | 0.8% | -21.81 pp | 2 |
| BBAS3.SA | -1.06% | -1.49 | 1.1% | +10.71 pp | 2 |
| BBDC4.SA | 4.99% | 2.07 | 1.0% | -13.93 pp | 2 |
| CYRE3.SA | 0.90% | 0.56 | 0.8% | +16.55 pp | 2 |
| ITUB4.SA | 0.30% | 0.27 | 0.8% | -19.37 pp | 2 |
| LREN3.SA | 0.00% | 0.00 | 0.0% | +14.55 pp | 0 |
| RADL3.SA | 8.53% | 1.10 | 3.9% | -12.95 pp | 2 |
| RENT3.SA | -0.87% | -1.31 | 0.9% | +2.71 pp | 2 |
| SUZB3.SA | -1.16% | -1.55 | 1.2% | +18.21 pp | 2 |
| WEGE3.SA | -0.12% | -0.13 | 0.8% | -4.78 pp | 2 |


#### Código-fonte (`algorithms/rsi_reversion.py`)

```python
# RSI pullback in uptrend + TA-Lib bullish reversal candle confirmation
import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason, add_bullish_reversal_column


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


def _has_bullish_reversal(df):
    if df["bullish_reversal"].iloc[-1]:
        return True
    if len(df) >= 2 and df["bullish_reversal"].iloc[-2]:
        return True
    return False


def process_data(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma50_slope"] = df["sma50"].diff(5)
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["std20"] = df["Close"].rolling(window=20).std()
    df["bb_upper"] = df["sma20"] + 2 * df["std20"]
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    add_bullish_reversal_column(df)
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    rsi = df["rsi14"].iloc[-1]
    sma21 = df["sma21"].iloc[-1]
    bb_upper = df["bb_upper"].iloc[-1]
    stop_mult = 2.0 if price < sma21 else 2.5
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - stop_mult * atr),
        ("Chandelier trail", price < trail),
        ("Bollinger take profit", price >= bb_upper and rsi > 62),
        ("RSI overbought", rsi > 72),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    rsi = df["rsi14"].iloc[-1]
    rsi_limit = 40
    if entry_filters_active(portfolio):
        y = portfolio.get("_entry_reluctance", 1.0)
        rsi_limit = 40 - max(0.0, y - 1.0) * 7
    if rsi > rsi_limit:
        return entry_gate(False, portfolio)
    if price < df["sma50"].iloc[-1]:
        return entry_gate(False, portfolio)
    if df["sma50_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        if not _has_bullish_reversal(df) and rsi >= 32:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf"):
            if price > sold * 1.03:
                return entry_gate(False, portfolio)
            if sold * 0.96 < price < sold * 1.05:
                return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
```

### SMA-20 trend (Medium-term trend following)

A slower cousin of the SMA-8 strategy. The 20-day average filters out more noise and targets sustained moves where medium- and long-term trends align.

- **Indicadores:** SMA-20, SMA-50, 2-bar SMA-20 slope, ATR(14), 22-day high.
- **Lógica de compra:** Price above SMA-20 with rising 2-bar slope; SMA-20 above SMA-50; price anchored within 2–4% of SMA-50; not chasing more than ~4% above SMA-20; relaxed cooldown after sells.
- **Lógica de venda:** ATR stop-loss (3× ATR), chandelier trail, or break below SMA-50 — no commission gate.

#### Performance ajustada ao risco

| Métrica | Valor |
| --- | ---: |
| Score de risco | 60 |
| Retorno médio | 2.06% |
| C&M médio | 2.18% |
| Sharpe | 0.22 (C&M 0.39) |
| Drawdown máximo | 3.0% (C&M 26.0%) |
| Captura de baixa | 5.25 |
| Tempo no mercado | 7.8% |
| Runs sem trades | 5 / 10 |
| Superou C&M | 5 / 10 |

#### Performance por regime

| Alta | Baixa | Lateral | Alta vol. |
| --- | ---: | ---: | ---: |
| 4.4% | 0.0% | -1.1% | 0.5% |

#### Atribuição de saídas

| Razão | PnL médio % |
| --- | ---: |
| Trailing chandelier | +2.06% |

Motor de sinal: +0.00% · Motor de risco: +2.06%

#### Resultados por papel

| Papel | Retorno | Sharpe | DD máx. | vs C&M | Trades |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 0.00% | 0.00 | 0.0% | -21.94 pp | 0 |
| BBAS3.SA | -2.62% | -0.55 | 7.1% | +9.15 pp | 4 |
| BBDC4.SA | 2.83% | 0.65 | 3.6% | -16.09 pp | 2 |
| CYRE3.SA | 8.66% | 0.90 | 8.5% | +24.31 pp | 2 |
| ITUB4.SA | 13.09% | 1.50 | 6.2% | -6.59 pp | 6 |
| LREN3.SA | 0.00% | 0.00 | 0.0% | +14.55 pp | 0 |
| RADL3.SA | 0.00% | 0.00 | 0.0% | -21.48 pp | 0 |
| RENT3.SA | 0.00% | 0.00 | 0.0% | +3.57 pp | 0 |
| SUZB3.SA | -1.37% | -0.28 | 4.1% | +17.99 pp | 4 |
| WEGE3.SA | 0.00% | 0.00 | 0.0% | -4.66 pp | 0 |


#### Código-fonte (`algorithms/sma20_trend.py`)

```python
import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["sma20"] = df["Close"].rolling(window=20).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma20_slope"] = df["sma20"].diff(2)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - 30.0 * atr),
        ("Chandelier trail", price < trail),
        ("SMA-50 break", price < df["sma50"].iloc[-1]),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma20 = df["sma20"].iloc[-1]
    sma50 = df["sma50"].iloc[-1]
    if price <= sma20 or df["sma20_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if sma20 < sma50:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        if price < sma50 * 0.98 or price > sma50 * 1.04:
            return entry_gate(False, portfolio)
        if price > sma20 * 1.04:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf") and sold * 0.94 < price < sold * 1.06:
            return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
```

### SMA crossover (Dual moving-average crossover)

A well-known momentum signal: when a fast average crosses above a slow one, momentum may be shifting bullish. Requires a rising SMA-50 trend and RSI not overbought.

- **Indicadores:** SMA-8, SMA-21, SMA-50, SMA-50 slope, RSI(14), ATR(14), 22-day high.
- **Lógica de compra:** Fresh bullish cross — SMA-8 just crossed above SMA-21; price above SMA-50; SMA-50 not in meaningful decline (> −0.5% over 5 bars); RSI ≤ 65.
- **Lógica de venda:** Adaptive ATR stop (2× below SMA-21, else 3×), chandelier trail, or bearish cross — no commission gate on technical exits.

#### Performance ajustada ao risco

| Métrica | Valor |
| --- | ---: |
| Score de risco | 38 |
| Retorno médio | 2.88% |
| C&M médio | 2.18% |
| Sharpe | -0.02 (C&M 0.48) |
| Drawdown máximo | 4.9% (C&M 26.0%) |
| Captura de baixa | 7.57 |
| Tempo no mercado | 11.2% |
| Runs sem trades | 3 / 10 |
| Superou C&M | 6 / 10 |

#### Performance por regime

| Alta | Baixa | Lateral | Alta vol. |
| --- | ---: | ---: | ---: |
| 20.5% | -0.5% | 3.9% | -9.0% |

#### Atribuição de saídas

| Razão | PnL médio % |
| --- | ---: |
| Trailing chandelier | +2.80% |

Motor de sinal: +0.00% · Motor de risco: +2.80%

#### Resultados por papel

| Papel | Retorno | Sharpe | DD máx. | vs C&M | Trades |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | -2.73% | -0.91 | 4.0% | -24.67 pp | 4 |
| BBAS3.SA | -2.16% | -1.53 | 2.2% | +9.62 pp | 2 |
| BBDC4.SA | -1.14% | -0.20 | 7.0% | -20.06 pp | 4 |
| CYRE3.SA | 9.98% | 1.05 | 8.5% | +25.63 pp | 2 |
| ITUB4.SA | 0.00% | 0.00 | 0.0% | -19.68 pp | 0 |
| LREN3.SA | -12.28% | -2.29 | 12.3% | +2.27 pp | 4 |
| RADL3.SA | 21.24% | 1.55 | 9.8% | -0.23 pp | 4 |
| RENT3.SA | 0.00% | 0.00 | 0.0% | +3.57 pp | 0 |
| SUZB3.SA | 0.00% | 0.00 | 0.0% | +19.36 pp | 0 |
| WEGE3.SA | 15.84% | 2.17 | 5.5% | +11.18 pp | 4 |


#### Código-fonte (`algorithms/sma_crossover.py`)

```python
import pandas as pd
from algorithm_helpers import entry_gate, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma50_slope"] = df["sma50"].diff(5)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    stop_mult = 20.0 if price < df["sma21"].iloc[-1] else 30.0
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - stop_mult * atr),
        ("Chandelier trail", price < trail),
        ("Bearish cross", df["sma8"].iloc[-1] < df["sma21"].iloc[-1]),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    if len(df) < 2:
        return entry_gate(False, portfolio)
    sma50 = df["sma50"].iloc[-1]
    if price < sma50:
        return entry_gate(False, portfolio)
    if df["sma50_slope"].iloc[-1] < -sma50 * 0.005:
        return entry_gate(False, portfolio)
    if df["sma8"].iloc[-1] <= df["sma21"].iloc[-1]:
        return entry_gate(False, portfolio)
    if df["sma8"].iloc[-2] > df["sma21"].iloc[-2]:
        return entry_gate(False, portfolio)
    if df["rsi14"].iloc[-1] > 65:
        return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
```

### SMA-8 trend (Short-term trend following)

Rides early uptrends using a fast 8-day simple moving average (SMA). The idea is to enter when price is already above short- and medium-term averages and the fast average is still rising — a classic “trade with the trend” setup.

- **Indicadores:** SMA-8, SMA-21, SMA-50, 2-bar SMA-8 slope, Wilder ATR(14), 22-day high.
- **Lógica de compra:** Price above SMA-8 with a positive 2-bar slope; price above SMA-21 and SMA-50; dynamic extension cap above SMA-8 (tightens late-window); cooldown after recent sells. Uses reluctant entry to skip marginal signals.
- **Lógica de venda:** ATR stop-loss (3× ATR below entry), chandelier trail (22-day high − 2.5× ATR), or close below SMA-21 — technical exits fire regardless of commission.

#### Performance ajustada ao risco

| Métrica | Valor |
| --- | ---: |
| Score de risco | 4 |
| Retorno médio | 2.48% |
| C&M médio | 2.18% |
| Sharpe | 0.11 (C&M 0.39) |
| Drawdown máximo | 9.0% (C&M 26.0%) |
| Captura de baixa | 21.27 |
| Tempo no mercado | 29.2% |
| Runs sem trades | 0 / 10 |
| Superou C&M | 6 / 10 |

#### Performance por regime

| Alta | Baixa | Lateral | Alta vol. |
| --- | ---: | ---: | ---: |
| 11.7% | -6.2% | 31.0% | -6.7% |

#### Atribuição de saídas

| Razão | PnL médio % |
| --- | ---: |
| Rompimento MM | +1.70% |
| Trailing chandelier | +0.95% |

Motor de sinal: +1.70% · Motor de risco: +0.95%

#### Resultados por papel

| Papel | Retorno | Sharpe | DD máx. | vs C&M | Trades |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABEV3.SA | 4.30% | 0.53 | 7.8% | -17.64 pp | 8 |
| BBAS3.SA | -6.40% | -0.73 | 11.8% | +5.38 pp | 8 |
| BBDC4.SA | 7.38% | 0.85 | 5.8% | -11.54 pp | 6 |
| CYRE3.SA | 1.86% | 0.18 | 8.6% | +17.51 pp | 8 |
| ITUB4.SA | 8.90% | 0.93 | 7.0% | -10.78 pp | 8 |
| LREN3.SA | -8.45% | -1.26 | 8.4% | +6.10 pp | 6 |
| RADL3.SA | 11.08% | 0.77 | 10.7% | -10.39 pp | 10 |
| RENT3.SA | 6.19% | 0.51 | 12.0% | +9.77 pp | 8 |
| SUZB3.SA | -8.87% | -1.65 | 10.1% | +10.49 pp | 8 |
| WEGE3.SA | 8.81% | 0.98 | 7.6% | +4.14 pp | 6 |


#### Código-fonte (`algorithms/sma8_trend.py`)

```python
import pandas as pd
from algorithm_helpers import entry_gate, entry_filters_active, first_sell_reason


def _atr(df, window=14):
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


def process_data(df):
    df["sma8"] = df["Close"].rolling(window=8).mean()
    df["sma21"] = df["Close"].rolling(window=21).mean()
    df["sma50"] = df["Close"].rolling(window=50).mean()
    df["sma8_slope"] = df["sma8"].diff(2)
    df["atr14"] = _atr(df)
    df["high22"] = df["High"].rolling(window=22).max()
    return df.dropna()


def check_selling_conditions(df, price, portfolio, comission):
    entry = portfolio["price_bought"]
    if not entry:
        return False
    atr = df["atr14"].iloc[-1]
    trail = df["high22"].iloc[-1] - 2.5 * atr
    reason = first_sell_reason([
        ("ATR stop", price < entry - 30.0 * atr),
        ("Chandelier trail", price < trail),
        ("SMA break", price < df["sma21"].iloc[-1]),
    ], portfolio)
    if reason:
        portfolio["_last_exit_reason"] = reason
        return True
    return False


def check_buying_conditions(df, price, portfolio):
    sma8 = df["sma8"].iloc[-1]
    if price <= sma8 or df["sma8_slope"].iloc[-1] <= 0:
        return entry_gate(False, portfolio)
    if price < df["sma21"].iloc[-1] or price < df["sma50"].iloc[-1]:
        return entry_gate(False, portfolio)
    if entry_filters_active(portfolio):
        y = portfolio.get("_entry_reluctance", 1.0)
        ext_limit = 1.035 - max(0.0, y - 1.0) * 0.008
        if price > sma8 * ext_limit:
            return entry_gate(False, portfolio)
        sold = portfolio["price_sold"]
        if sold != float("inf") and sold * 0.96 < price < sold * 1.05:
            return entry_gate(False, portfolio)
    return entry_gate(True, portfolio)
```

## Todos os resultados dos testes

| # | Algoritmo | Papel | Retorno | Sharpe | DD máx. | vs C&M | Posição |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | SMA-8 trend | ITUB4.SA | 8.90% | 0.93 | 7.0% | -10.78 pp | Vendido |
| 2 | SMA-8 trend | BBDC4.SA | 7.38% | 0.85 | 5.8% | -11.54 pp | Vendido |
| 3 | SMA-8 trend | RADL3.SA | 11.08% | 0.77 | 10.7% | -10.39 pp | Vendido |
| 4 | SMA-8 trend | WEGE3.SA | 8.81% | 0.98 | 7.6% | +4.14 pp | Vendido |
| 5 | SMA-8 trend | ABEV3.SA | 4.30% | 0.53 | 7.8% | -17.64 pp | Vendido |
| 6 | SMA-8 trend | BBAS3.SA | -6.40% | -0.73 | 11.8% | +5.38 pp | Vendido |
| 7 | SMA-8 trend | RENT3.SA | 6.19% | 0.51 | 12.0% | +9.77 pp | Vendido |
| 8 | SMA-8 trend | LREN3.SA | -8.45% | -1.26 | 8.4% | +6.10 pp | Vendido |
| 9 | SMA-8 trend | CYRE3.SA | 1.86% | 0.18 | 8.6% | +17.51 pp | Vendido |
| 10 | SMA-8 trend | SUZB3.SA | -8.87% | -1.65 | 10.1% | +10.49 pp | Vendido |
| 11 | SMA-20 trend | ITUB4.SA | 13.09% | 1.50 | 6.2% | -6.59 pp | Vendido |
| 12 | SMA-20 trend | BBDC4.SA | 2.83% | 0.65 | 3.6% | -16.09 pp | Vendido |
| 13 | SMA-20 trend | RADL3.SA | 0.00% | 0.00 | 0.0% | -21.48 pp | Neutro |
| 14 | SMA-20 trend | WEGE3.SA | 0.00% | 0.00 | 0.0% | -4.66 pp | Neutro |
| 15 | SMA-20 trend | ABEV3.SA | 0.00% | 0.00 | 0.0% | -21.94 pp | Neutro |
| 16 | SMA-20 trend | BBAS3.SA | -2.62% | -0.55 | 7.1% | +9.15 pp | Vendido |
| 17 | SMA-20 trend | RENT3.SA | 0.00% | 0.00 | 0.0% | +3.57 pp | Neutro |
| 18 | SMA-20 trend | LREN3.SA | 0.00% | 0.00 | 0.0% | +14.55 pp | Neutro |
| 19 | SMA-20 trend | CYRE3.SA | 8.66% | 0.90 | 8.5% | +24.31 pp | Vendido |
| 20 | SMA-20 trend | SUZB3.SA | -1.37% | -0.28 | 4.1% | +17.99 pp | Vendido |
| 21 | SMA crossover | ITUB4.SA | 0.00% | 0.00 | 0.0% | -19.68 pp | Neutro |
| 22 | SMA crossover | BBDC4.SA | -1.14% | -0.20 | 7.0% | -20.06 pp | Vendido |
| 23 | SMA crossover | RADL3.SA | 21.24% | 1.55 | 9.8% | -0.23 pp | Vendido |
| 24 | SMA crossover | WEGE3.SA | 15.84% | 2.17 | 5.5% | +11.18 pp | Vendido |
| 25 | SMA crossover | ABEV3.SA | -2.73% | -0.91 | 4.0% | -24.67 pp | Vendido |
| 26 | SMA crossover | BBAS3.SA | -2.16% | -1.53 | 2.2% | +9.62 pp | Vendido |
| 27 | SMA crossover | RENT3.SA | 0.00% | 0.00 | 0.0% | +3.57 pp | Neutro |
| 28 | SMA crossover | LREN3.SA | -12.28% | -2.29 | 12.3% | +2.27 pp | Vendido |
| 29 | SMA crossover | CYRE3.SA | 9.98% | 1.05 | 8.5% | +25.63 pp | Vendido |
| 30 | SMA crossover | SUZB3.SA | 0.00% | 0.00 | 0.0% | +19.36 pp | Neutro |
| 31 | RSI reversion | ITUB4.SA | 0.30% | 0.27 | 0.8% | -19.37 pp | Vendido |
| 32 | RSI reversion | BBDC4.SA | 4.99% | 2.07 | 1.0% | -13.93 pp | Vendido |
| 33 | RSI reversion | RADL3.SA | 8.53% | 1.10 | 3.9% | -12.95 pp | Vendido |
| 34 | RSI reversion | WEGE3.SA | -0.12% | -0.13 | 0.8% | -4.78 pp | Vendido |
| 35 | RSI reversion | ABEV3.SA | 0.13% | 0.12 | 0.8% | -21.81 pp | Vendido |
| 36 | RSI reversion | BBAS3.SA | -1.06% | -1.49 | 1.1% | +10.71 pp | Vendido |
| 37 | RSI reversion | RENT3.SA | -0.87% | -1.31 | 0.9% | +2.71 pp | Vendido |
| 38 | RSI reversion | LREN3.SA | 0.00% | 0.00 | 0.0% | +14.55 pp | Neutro |
| 39 | RSI reversion | CYRE3.SA | 0.90% | 0.56 | 0.8% | +16.55 pp | Vendido |
| 40 | RSI reversion | SUZB3.SA | -1.16% | -1.55 | 1.2% | +18.21 pp | Vendido |
| 41 | 20-day breakout | ITUB4.SA | 4.85% | 1.91 | 3.2% | -14.83 pp | Vendido |
| 42 | 20-day breakout | BBDC4.SA | 5.33% | 2.24 | 2.2% | -13.59 pp | Vendido |
| 43 | 20-day breakout | RADL3.SA | -1.97% | -0.81 | 3.1% | -23.44 pp | Vendido |
| 44 | 20-day breakout | WEGE3.SA | 2.51% | 1.12 | 1.6% | -2.15 pp | Vendido |
| 45 | 20-day breakout | ABEV3.SA | 1.72% | 0.92 | 2.1% | -20.21 pp | Vendido |
| 46 | 20-day breakout | BBAS3.SA | 8.58% | 2.83 | 1.6% | +20.35 pp | Vendido |
| 47 | 20-day breakout | RENT3.SA | 0.32% | 0.20 | 1.6% | +3.90 pp | Vendido |
| 48 | 20-day breakout | LREN3.SA | 0.63% | 0.33 | 2.2% | +15.18 pp | Vendido |
| 49 | 20-day breakout | CYRE3.SA | 0.00% | 0.00 | 0.0% | +15.65 pp | Neutro |
| 50 | 20-day breakout | SUZB3.SA | 0.00% | 0.00 | 0.0% | +19.36 pp | Neutro |

## Definições de métricas

### Eficiência de risco
**Guia da seção:** Sharpe e captura de alta ↑ melhor · Drawdown máx. ↓ melhor · Captura de baixa ↓ melhor (seletiva) · Runs sem trades ↓ melhor · Tabela: retorno e Sharpe ↑ · volatilidade e drawdown máx. ↓.
**Orientação:** Somente contexto
Métricas de risco do portfólio, média de todos os runs do benchmark vs comprar e manter nos mesmos papéis e janela.

### Análise de exposição
**Guia da seção:** Baixa exposição = muito em caixa, não timing seletivo. Captura de alta ↑ melhor · Captura de baixa ↓ melhor (seletiva) · Runs sem trades ↓ melhor.
**Orientação:** Somente contexto
Quanto tempo cada estratégia ficou posicionada vs em caixa. Baixa exposição com baixa captura costuma indicar redução de risco por estar fora do mercado.

### Sinal vs motor de risco
**Guia da seção:** Retorno e captura de alta ↑ melhor · DD máx. ↓ melhor · Exposição: contexto (baixa = menos investido) · Δ retorno vs A: sinalado (± vs só sinal).
**Orientação:** Somente contexto
Três modos experimentais por algoritmo: A só sinal, B adiciona saídas de risco, C é a estratégia completa com filtros de entrada.

### Contexto de mercado
**Guia da seção:** Retorno do benchmark ↑ melhor · Superar comprar e manter: contagem maior é melhor.
**Orientação:** Somente contexto
Retornos do período para Ibovespa, USD/BRL e a matriz de testes — mostra se a janela foi amplamente altista ou mista.

### Algoritmos
**Guia da seção:** Retorno, Sharpe, captura de alta, score de risco e valor de proteção ↑ melhor · DD máx. e captura de baixa ↓ melhor · vs C&M: excedente com sinal. Tabela por papel: retorno e Sharpe ↑ · DD máx. ↓ · vs C&M sinalado.
**Orientação:** Somente contexto
Performance, teoria e código-fonte de cada estratégia no catálogo do benchmark.

### Testes individuais
**Guia da seção:** Retorno e valor de proteção ↑ melhor · vs benchmarks: excedente com sinal.
**Orientação:** Somente contexto
Saída completa do backtest para cada combinação algoritmo × papel na matriz.

### Performance por regime
**Orientação:** Somente contexto
Retornos diários anualizados da estratégia agrupados por rótulos heurísticos: alta, baixa, lateral, alta volatilidade.

### Atribuição de saídas
**Orientação:** Somente contexto
PnL % por round-trip agrupado pela primeira razão de saída disparada (ATR, chandelier, saídas de sinal, etc.).

### Sharpe
**Orientação:** ↑ melhor
**Meta:** ≥ 0,5 ou superar C&M
Retorno anualizado menos taxa livre de risco 0%, dividido pela volatilidade anualizada dos retornos diários do portfólio (252 pregões). Calculado a partir da curva de patrimônio simulada.

### Sharpe comprar e manter
**Orientação:** ↑ melhor
Mesma fórmula de Sharpe aplicada à curva de comprar e manter nas mesmas datas da estratégia.

### Drawdown máximo
**Orientação:** ↓ melhor
**Meta:** ≪ comprar e manter
Maior queda pico-a-vale no patrimônio durante a janela, em percentual positivo. Calculado barra a barra a partir de caixa mais posição marcada a mercado.

### Drawdown máx. comprar e manter
**Orientação:** ↓ melhor
Drawdown máximo na curva alinhada de comprar e manter (100% investido desde a primeira barra).

### Captura de baixa
**Orientação:** Meta 20–40% (participar de parte das perdas, não todas)
**Meta:** 20–40%
Nos dias em que o retorno diário de comprar e manter é negativo: retorno médio diário da estratégia dividido pelo de comprar e manter, × 100. 100% = absorveu todas as perdas; 7% ≈ evitou a maior parte.

### Captura de alta
**Orientação:** Meta 50–70% (participar dos ganhos mantendo defesa)
**Meta:** 50–70%
Nos dias em que o retorno diário de comprar e manter é positivo: retorno médio diário da estratégia dividido pelo de comprar e manter, × 100. 100% = capturou todos os ganhos.

### Tempo no mercado
**Orientação:** Compare com ~100% comprar e manter; % baixo costuma significar muito em caixa
**Meta:** 15–40%
Barras com pelo menos uma ação ÷ total de barras na janela do backtest × 100.

### Exposição
**Orientação:** Igual ao tempo no mercado
**Meta:** 15–40%
Barras posicionadas ÷ total de barras × 100. Comprar e manter ≈ 100%.

### Runs sem trades
**Orientação:** ↓ melhor
Quantidade de backtests em que a estratégia nunca entrou em posição (0 compras e 0 vendas).

### Retorno
**Orientação:** ↑ melhor
(Patrimônio final − saldo inicial) ÷ saldo inicial × 100. Inclui caixa e posição aberta no último fechamento.

### Retorno comprar e manter
**Orientação:** ↑ melhor
Retorno de comprar no primeiro fechamento e manter até o último, com o mesmo saldo inicial.

### Volatilidade (an.)
**Orientação:** ↓ melhor
**Meta:** ≪ comprar e manter
Desvio padrão dos retornos logarítmicos diários na curva de patrimônio × √252, em percentual.

### Média de trades
**Orientação:** Somente contexto
Média de execuções de compra mais venda por papel (round trips ≈ vendas).

### Score de risco
**Orientação:** ↑ melhor
**Meta:** ≥ 70
Composto 0–100: 40% redução normalizada de drawdown vs C&M, 30% redução de volatilidade, 30% melhora de Sharpe — ranqueado entre os cinco algoritmos deste benchmark.

### Valor de proteção
**Orientação:** ↑ melhor
**Meta:** > 0 pp
Composto narrativo (pp): (DD máx. C&M − DD máx. estratégia) + (vol. C&M − vol. estratégia) − max(0, retorno C&M − retorno estratégia). Não é alpha de Jensen.

### vs comprar e manter
**Orientação:** Excedente com sinal (+ supera C&M)
Retorno da estratégia menos retorno de comprar e manter no mesmo papel e janela, em pontos percentuais.

### Superou comprar e manter
**Orientação:** ↑ melhor
Número de runs em que o retorno da estratégia superou comprar e manter.

### Superou Ibovespa
**Orientação:** ↑ melhor
Runs em que o retorno da estratégia superou o retorno do Ibovespa (^BVSP) no período.

### Superou USD/BRL
**Orientação:** ↑ melhor
Runs em que o retorno da estratégia superou a variação do USD/BRL no período (indexado).

### Ibovespa
**Orientação:** Somente contexto
Variação percentual do ^BVSP do primeiro ao último fechamento na janela do benchmark.

### USD/BRL
**Orientação:** Somente contexto
Variação percentual do USDBRL=X na janela (BRL por USD).

### Testes executados
**Orientação:** Somente contexto
Total de backtests: algoritmos × papéis na matriz do benchmark.

### Δ retorno vs A
**Orientação:** ↑ melhor
Retorno médio desta versão da decomposição menos a Versão A (só sinal) para o mesmo algoritmo.

### Versão
**Orientação:** Somente contexto
A = sinais centrais · B = A + ATR/chandelier · C = estratégia completa com filtros e entrada relutante.

### Estratégia
**Orientação:** Somente contexto
Nome do algoritmo no catálogo do benchmark.

### Papel
**Orientação:** Somente contexto
Ticker B3 testado neste run.

### Algoritmo
**Orientação:** Somente contexto
Script de estratégia executado neste backtest.

### Janela
**Orientação:** Somente contexto
Período e intervalo de barras do yfinance (ex.: 1y / 1d) da simulação.

### Intervalo de datas
**Orientação:** Somente contexto
Primeira e última data negociável da série após o warm-up dos indicadores.

### Trades
**Orientação:** Somente contexto
Total de compras mais vendas no run.

### Posição
**Orientação:** Somente contexto
Estado final: Comprado (com ações), Vendido (zerado após operar) ou Neutro (nunca entrou).

### Alta
**Orientação:** ↑ melhor
Retorno diário médio anualizado em barras classificadas como alta (fechamento > MM-50 com inclinação positiva).

### Baixa
**Orientação:** Menos negativo pode ser defensivo
Retorno anualizado em barras de baixa (fechamento < MM-50 com inclinação negativa).

### Lateral
**Orientação:** Somente contexto
Retorno anualizado em barras não classificadas como alta, baixa ou alta volatilidade.

### Alta vol.
**Orientação:** Somente contexto
Retorno anualizado quando o ATR(14) está acima do percentil 70 da janela.

### PnL médio %
**Orientação:** ↑ melhor
Soma do PnL % por round-trip atribuída a cada razão de saída, média entre runs do algoritmo.

### Motor de sinal
**Orientação:** ↑ melhor
PnL % agregado de saídas classificadas como sinal (rompimento de MM, RSI, breakout, etc.).

### Motor de risco
**Orientação:** ↑ melhor
PnL % agregado de saídas classificadas como risco (stop ATR, trailing chandelier).

### Melhor · Pior
**Orientação:** Somente contexto
Maior e menor retorno % da estratégia entre os dez papéis deste algoritmo.

### Runs lucrativos
**Orientação:** ↑ melhor
Runs com ganho absoluto positivo em moeda.

### vs Ibovespa
**Orientação:** ↑ melhor
Retorno da estratégia menos retorno do Ibovespa no período, em pontos percentuais.

### vs USD/BRL
**Orientação:** ↑ melhor
Retorno da estratégia menos variação do USD/BRL no período, em pontos percentuais.

### Saldo inicial
**Orientação:** Somente contexto
Caixa simulado inicial (R$) para cada run do benchmark.

### Performance do papel
**Orientação:** Somente contexto
Retorno de comprar e manter deste papel no intervalo do run.

### Perfil de risco
**Orientação:** Somente contexto
Sharpe, drawdown máximo e captura de baixa do run vs comprar e manter.

### Final
**Orientação:** Somente contexto
Ações finais e saldo em caixa após a última barra.

### Dispersão risco vs retorno
**Orientação:** Somente contexto
Cada ponto = retorno médio (Y) vs drawdown máximo médio (X) de um algoritmo. Inferior direito = defensivo; superior esquerdo = fraco.

### Score de redução de risco
**Orientação:** ↑ melhor
Gráfico de barras do score 0–100 ranqueando os algoritmos.

### Curva de drawdown
**Orientação:** Somente contexto
Drawdown diário % do pico para o algoritmo com melhor score de risco vs comprar e manter em um run representativo.

### Sharpe móvel
**Orientação:** Somente contexto
Sharpe móvel de 90 pregões a partir dos retornos diários (amostra de runs por algoritmo).

### Gráfico de contexto de mercado
**Orientação:** Somente contexto
Barras com retorno médio de estratégias, comprar e manter, Ibovespa e USD/BRL no período.

### Ibovespa indexado
**Orientação:** Somente contexto
Fechamento do ^BVSP reindexado a 100 na primeira barra da janela.

### USD/BRL indexado
**Orientação:** Somente contexto
USDBRL=X reindexado a 100 na primeira barra.

### Comparação de retorno bruto
**Orientação:** Somente contexto
Barras agrupadas do retorno médio da estratégia vs comprar e manter por algoritmo.
