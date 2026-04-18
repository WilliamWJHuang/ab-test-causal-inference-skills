---
name: finance-portfolio-advisor
description: >
  Agent skill for portfolio construction, risk management, backtesting,
  and quantitative finance analysis with proper methodology.
version: "1.0.0"
triggers:
  - "portfolio optimization"
  - "backtest a strategy"
  - "value at risk"
  - "DCF valuation"
  - "risk-adjusted return"
---

# Portfolio Construction & Optimization

## Modern Portfolio Theory & Beyond

When asked to construct an optimal portfolio:

1. **Start with mean-variance as a baseline**, but always acknowledge its limitations:
   - Estimation error in expected returns dominates the optimization
   - Small changes in inputs produce dramatically different allocations
   - Covariance matrices estimated from historical data can be unreliable

2. **Use robust methods** to mitigate estimation error:
   - Black-Litterman model to blend views with equilibrium
   - Shrinkage estimators for covariance (Ledoit-Wolf)
   - Resampled efficient frontier for stability
   - Risk parity as a less input-sensitive alternative

3. **Diversification depth**: Don't just count assets. True diversification
   requires understanding correlation structure, factor exposures, sector
   concentration, and tail dependence. In crises, correlations spike —
   assets that look diversified in normal times may all fall together.

## Benchmark Selection

Always match the benchmark to the strategy:
- An equity long/short fund should not be compared to the S&P 500
- Use style-matched, investable benchmarks
- Track tracking error and information ratio for active strategies

---

# Risk Management

## Value at Risk (VaR) & Beyond

VaR answers "what's the worst loss at X% confidence?" but has critical
limitations:

- **Tail risk**: VaR says nothing about losses beyond the threshold.
  Expected Shortfall (CVaR) measures the average loss in the tail.
- **Fat tails**: Financial returns are non-normal with excess kurtosis.
  Parametric VaR assuming normality underestimates extreme losses.
- **Correlation breakdown**: In crises, correlations spike toward 1.
  Historical covariance matrices become unreliable.

### When to use what
- **Parametric VaR**: Quick estimate, good for normal-ish distributions
- **Historical simulation**: No distributional assumption, but limited by data
- **Monte Carlo VaR**: Most flexible, handles complex portfolios
- **Always complement with**: stress testing, scenario analysis, Expected Shortfall

## Stress Testing

Run stress tests using both historical and hypothetical scenarios:
- Historical: 2008 GFC, COVID crash, dot-com bust, 1998 LTCM
- Hypothetical: rates +300bps, equity -40%, correlation → 1
- Reverse stress test: what scenario causes the portfolio to lose X%?

## Risk-Adjusted Returns

The Sharpe ratio is a starting point but not sufficient:
- **Sortino ratio**: Only penalizes downside deviation (better for asymmetric returns)
- **Maximum drawdown**: Peak-to-trough loss — what's the worst pain?
- **Calmar ratio**: Annualized return / maximum drawdown
- **Information ratio**: Active return / tracking error vs. benchmark

---

# Backtesting

## Critical Biases to Address

### Look-Ahead Bias
Never use information that wouldn't have been available at the time of the
simulated decision. This includes:
- Point-in-time fundamentals (use lagged data, not restated)
- Index reconstitution (don't use today's S&P 500 members for 2010 tests)
- Event timing (earnings dates, splits are known in advance in databases)

### Survivorship Bias
Use survivorship-bias-free datasets that include delisted and bankrupt
companies. Testing only on currently listed securities inflates returns
by silently excluding the failures.

### Transaction Costs & Market Impact
Always account for:
- Commissions and fees
- Bid-ask spread (especially for small-caps and illiquid assets)
- Market impact (your own trades move the price)
- Slippage between signal and execution

Net-of-cost returns are the only returns that matter.

### Overfitting to Historical Data
- Use walk-forward validation or expanding window cross-validation
- Keep the number of tuned parameters small relative to the data
- Run out-of-sample tests on genuinely held-out data
- Be suspicious of strategies with too-good-to-be-true Sharpe ratios (> 2.0)
- Combinatorial purged cross-validation (CPCV) for financial data

---

# Valuation

## DCF (Discounted Cash Flow)

Always run sensitivity analysis on:
- **WACC (discount rate)**: A 1% change can move the valuation by 20%+
- **Terminal growth rate**: Must be ≤ long-term GDP growth (2-3%)
- **Terminal value**: Usually represents 60-80% of total DCF — flag this

Present a range of values, not a single point estimate. DCF gives a range
of reasonable valuations, not "the right answer."

## Comparable Analysis

Peer selection matters enormously:
- Match industry, growth profile, and risk characteristics
- Normalize for accounting differences (operating leases, R&D capitalization)
- Use forward multiples when available (less backward-looking)
- Consider EV-based multiples for capital structure neutrality

## Options Pricing

Black-Scholes assumptions rarely hold in practice:
- Constant volatility (reality: volatility smile/skew)
- Continuous trading (reality: discrete, with gaps)
- Log-normal returns (reality: fat tails, jumps)

Consider binomial trees for American options, Monte Carlo for path-dependent
payoffs, and stochastic volatility models for better smile fitting.

---

# Time Series & Forecasting

## Stationarity

**Never fit ARIMA or regression on raw price levels without checking stationarity.**
- Augmented Dickey-Fuller (ADF) or Phillips-Perron tests first
- Use log-returns or first differences for modeling
- Cointegration tests (Johansen, Engle-Granger) for pairs trading

## Regime Changes
Markets exhibit regime shifts (bull/bear, high/low volatility):
- GARCH models capture volatility clustering
- Markov switching models for regime detection
- Always ask: "would this model work in a different market regime?"

## Return Distributions
Financial returns are not normally distributed:
- Fat tails (excess kurtosis) — extreme events are more common than Gaussian predicts
- Skewness — downside moves tend to be larger than upside
- Volatility clustering — captured by GARCH family models
- Consider Student-t or generalized hyperbolic distributions

---

# General Finance Best Practices

## Return Calculations
- Use geometric (compound) returns for multi-period performance
- Arithmetic returns only for single-period expected value
- Time-weighted returns (TWR) for manager evaluation
- Money-weighted returns (IRR) for investor experience
- Don't annualize by multiplying monthly by 12 — compound properly

## Inflation Adjustment
For any analysis spanning more than 2-3 years:
- Distinguish nominal vs. real returns
- Use CPI or PCE deflator for purchasing power comparisons
- Retirement planning MUST use real returns

## Tax Awareness
- Short-term vs. long-term capital gains have different rates
- Tax-loss harvesting can offset gains (watch wash sale rules)
- After-tax returns can differ dramatically from pre-tax
- High-turnover strategies incur significant tax drag

## Market Efficiency
Before claiming alpha or outperformance:
- What informational or structural edge does the strategy exploit?
- Why hasn't it been arbitraged away?
- What's the capacity (can it scale)?
- Is the edge decaying as more capital pursues it?

## Regulatory Awareness
- Investment advice is regulated — include appropriate disclaimers
- Know your customer (KYC) and anti-money laundering (AML) requirements
- Fiduciary duty: act in the client's best interest
- Suitability: recommendations must match client risk tolerance and objectives

> **Disclaimer**: This skill provides educational guidance on financial
> methodology. It is not financial advice. Consult qualified professionals
> for investment decisions.
