## ML / Agents Technical Specification (MVP)

### 1. Overview

The ML/agents layer for the MVP is **deterministic with an optional RL (DQN) policy**, designed to be:

- Simple and explainable.
- Implemented as pure Python modules callable from the FastAPI backend.
- **RL-ready**: interfaces are defined so that a learned policy can later replace the heuristic Investment Agent.

Components:

- Risk Agent (logic-based).
- Goal Feasibility Agent (math-based).
- Investment Agent (heuristic).
- Strategy Agent (heuristic fallback, **optional tinygrad DQN**).
- Narrator (LLM-based report generator; **Gemini optional**, mock fallback).

---

### 2. Where this is implemented

The implementation lives in:

- `backend/agents/` (agents, RL env, tinygrad DQN, state encoder)
- `backend/services/prognosis_service.py` (orchestration + DB read/write)
- `backend/api/prognosis.py` (endpoints)
- `backend/integrations/llm_client.py` (Narrator LLM / fallback)

The authoritative orchestration flow for production is `generate_prognosis()` in `backend/services/prognosis_service.py`.

---

## Pipeline (implemented)

`DB models -> Risk/Goals/Allocation -> State Vector -> Strategy (DQN or heuristic) -> Narrator -> Persist report`

High-level flow:

1. Read `Profile`, `Account`, last-60-days `Transaction`, and `Goal` rows for the user.
2. Compute `monthly_income` and `monthly_savings` from last-30-days transactions.
3. Run:
   - `agents.risk_agent.compute_risk_metrics(...)`
   - `agents.goal_agent.evaluate_goals(...)`
   - `agents.investment_agent.recommend_allocation(...)` (uses macro state)
4. Build a 5D RL state vector via `agents.state_encoder.encode_state(...)`.
5. Pick a strategy action via `agents.strategy_agent.StrategyAgent.get_strategy(...)`:
   - If a trained model is available, use DQN argmax.
   - Otherwise, use the built-in heuristic policy.
6. Call the Narrator (`integrations.llm_client.generate_prognosis_report(...)`) to produce `report_json`.
7. Cache/update the latest report in DB (`PrognosisReport`) and apply rate limiting (`PrognosisUsage`).

### Methodologies
tinygrad

DQN (Deep Q Learning)
`state -> dense -> relu -> dense -> Q-values`

### Minimal RL model
* Q(s,a) = expected long-term financial health

**Training Loop**
observe state
choose action (epsilon-greedy)
simulate next state
compute reward
update Q network


### 3. Risk Agent

#### 3.1 Purpose
Measures how fragile the user is financially

Compute:
- Burn Rate (average monthly spending).
- Runway (months until liquid assets run out).
- Risk Capacity Score (0–100).

#### 3.2 Inputs
- Recent transactions (last 60 days). In production this is passed as a list of dicts with `amount`, `type`, `date`, `currency`.
- Liquid assets are passed as a list of dicts (bank + cash accounts) with `balance` and `currency`.
- `base_currency` (currently not used inside the function, but passed through).
- `monthly_income` (computed from last 30 days credits).

```python
def compute_risk_metrics(
    transactions: list[dict],
    liquid_accounts: list[dict],
    base_currency: str,
    monthly_income: float = 0.0,
) -> dict:
    ...
```

Assumptions:

- Only `debit` transactions count as spending for burn rate.
- Credits are not directly used for burn rate (but influence savings).

#### 3.3 Calculations (MVP)

1. **Total spend** over lookback:
   - Filter `transactions` to those with `type == 'debit'` and `date >= today - lookback_days`.
   - Sum `amount` to get `total_spend`.
2. **Average daily spend**:
   - `avg_daily_spend = total_spend / lookback_days`.
3. **Monthly Burn Rate**:
   - `burn_rate = avg_daily_spend * 30`.
4. **Runway**:
   - `liquid_assets = sum(account.balance for account in liquid_accounts)`.
   - If `burn_rate == 0`, set `runway_months = float('inf')`.
   - Else `runway_months = liquid_assets / burn_rate`.
5. **Stability ratio**:
   - Stability = income / expenses

#### 3.4 Output

```
risk_score =
  40 * normalize(runway)
+ 30 * normalize(stability)
+ 30 * savings_ratio
```
* normalize(x, min, max) = clamp((x - min)/(max - min), 0, 1)
  * runway: 0 - 12 months
  * stability: 0.5 - 2.0

```json
{
  "burn_rate": 42000,
  "runway_months": 5.2,
  "stability_ratio": 1.1,
  "savings_ratio": 0.18,
  "risk_score": 63,
  "risk_label": "Moderate"
}
```

---

### 4. Goal Feasibility Agent

#### 4.1 Purpose
Will the user actually reach their goals?

Assess for each goal whether it is:
- On Track.
- At Risk.
- Unrealistic.

Based on current savings vs what would be required to hit the target by the target date.

#### 4.2 Inputs
- `goals`: list of dicts with `id`, `name`, `target_amount`, `target_date`, `priority`
- `monthly_savings`: computed as (last-30-days credits - last-30-days debits)
- `current_savings`: current liquid balances sum (bank + cash)
- `expected_return`: annual return used as the mean for simulation (default `0.07`)

#### 4.3 Calculations (MVP)
For each goal:

1. Future Value:
  FV = current_savings*(1+r)^t + contribution * ((1+r)^t - 1)/r

2. compare:
  gap = goal_amount - FV

### Probability model (demo version)
We simulate uncertainty.

Run Monte Carlo 500 times with random returns.

Counts: success_rate = succesful_runs / total_runs

#### 4.4 Output
Per goal:

```json
{
  "goal_id": "...",
  "goal_name": "Retirement",
  "projected_value": 1_200_000,
  "success_probability": 0.72,
  "status": "at_risk",
  "goal_pressure": 1 - success_probability
}
```

Additional fields returned by the implementation:

- `required_monthly_savings`
- `actual_monthly_savings`

---

### 5. Macro State

#### 5.1 Purpose

Translate public indicators into a **discrete macro state** used by the Investment Agent.

The macro state is obtained via `integrations.market_client.get_macro_state()`.

Expected macro labels in the Investment Agent:

- `bull`
- `sideways`
- `bear`
- `recession`

---

### 6. Investment Agent (Heuristic)

#### 5.1 Purpose
What allocation matches this user?

Convert:
- Risk score (0–100).
- age
- goal_time_horizon
- market_volatility (<- Macro State Classifier)

Into a target **asset-class allocation**.
#### 5.2 Asset Classes (MVP)

- `cash`
- `debt`
- `equity`
- `other` (e.g., gold, crypto). *Only show what you recommend in output*

* Equity_ratio = 100 - age
adjusted by risk_score
adjusted by volatility

Allocations sum to 1.0.

#### 5.3 Inputs
```python
def recommend_allocation(
    risk_capacity_score: int,
    risk_appetite: str,
    goals_summary: list[dict],
    macro_state: str,
    age: int = 35,
    goal_time_horizon: int = 10,
) -> dict:
    ...
```

#### Two-plan output (capacity vs appetite)

The implementation returns:

- `recommended`: always present
- `aggressive_alternative`: present only when `risk_appetite == "aggressive"` and risk capacity is low (`risk_capacity_score/100 < 0.5`).

#### 6.8 Output

```json
{
  "recommended": {
    "equity": 0.55,
    "debt": 0.30,
    "cash": 0.10,
    "other": 0.05
  },
  "aggressive_alternative": {
    "equity": 0.70,
    "debt": 0.20,
    "cash": 0.05,
    "other": 0.05
  }
}
```

---

## 7. Strategy Agent (heuristic with optional DQN)

This agent consumes outputs from:

- Risk Agent output (`risk_metrics`)
- Goal Agent output (`goal_evaluations`)
- Investment Agent output (`allocation`)
- Savings rate (`savings_ratio` from Risk Agent)

### Strategy outputs (implemented)

The agent outputs one of the following discrete actions (see `agents/strategy_agent.py`):

- `keep_strategy`
- `increase_savings` (`delta: +5`)
- `reduce_savings` (`delta: -5`)
- `shift_to_equity` (`allocation_shift: {equity:+10, debt:-10}`)
- `shift_to_bonds` (`allocation_shift: {equity:-10, debt:+10}`)

### State vector (authoritative)

The RL state vector is produced by `agents.state_encoder.encode_state(...)` and is always:

`[risk, goal_feasibility, equity_ratio, monthly_savings_rate, runway]`

Where:

- `risk`: `risk_score / 100` clamped to `[0,1]`
- `goal_feasibility`: average of `success_probability` across goals, clamped to `[0,1]`
- `equity_ratio`: `allocation.recommended.equity`, clamped to `[0,1]`
- `monthly_savings_rate`: currently `savings_ratio` from risk metrics, clamped to `[0,1]`
- `runway`: `min(runway_months/12, 1.0)`

### Actions (DQN)

Discrete action space (0..4) aligned to the action mapping above.

### Reward (training env)
reward =
    0.01 * net_worth_change
  - 2 if runway < 3 else 0
  + 5 if goal_on_track else -3

Each episode: 5 - 10 simulated years (60-120 months)

Default training episodes: `1000` (see `agents/train_rl.py`).

### Recent RL Improvements (March 2026)

The RL training environment and evaluation pipeline have been significantly enhanced:

**1. Fixed Analytics Alignment**
- Fixed `risk_score` calculation in `risk_agent.py` to properly scale to [0, 100] range
- Aligned RL environment goal feasibility with paper-faithful future value calculations using compound interest formulas
- RL environment now uses the same risk calculation semantics as production `risk_agent.py`

**2. Market Regime Modeling**
The environment now includes dynamic market regimes that transition stochastically:
- **Normal**: 7% annual equity returns, 15% volatility, 4% debt returns
- **Bull**: 12% annual equity returns, 12% volatility, 3.5% debt returns  
- **Bear**: -5% annual equity returns, 20% volatility, 4.5% debt returns
- **Recession**: -15% annual equity returns, 25% volatility, 3% debt returns

Regimes transition every 12-36 months with weighted probabilities based on current state.

**3. Income/Expense Shocks**
The environment applies realistic financial variability:
- 5% monthly probability of shocks
- Income boost: 10-30% temporary increase
- Income loss: 20-40% temporary decrease
- Expense spike: 20-50% temporary increase

**4. Comprehensive Metrics Tracking**
Training now automatically saves:
- Episode rewards (raw and 50-episode moving average)
- Episode lengths
- Terminal balances
- Goal achievement rates
- Minimum runway per episode
- Epsilon decay history
- High-DPI plots (PNG and PDF) for paper figures
- JSON summary with statistics
- CSV file with detailed per-episode metrics

Output files in `backend/agents/models/`:
- `training_metrics.png` / `training_metrics.pdf`
- `training_summary.json`
- `training_metrics.csv`

**5. Evaluation Pipeline**
New evaluation script `agents/evaluate_rl.py` provides:
- Fixed evaluation set (100 scenarios by default)
- Baseline comparisons:
  - Heuristic strategy (from `strategy_agent.py`)
  - Keep-strategy baseline (always action 0)
  - Random baseline
- Statistical reporting (mean ± std)
- Comparison plots saved as PNG/PDF
- Evaluation results in `evaluation_results.json`

**6. Reproducibility**
- Training accepts `seed` parameter for reproducible experiments
- Multi-seed runs supported for statistical significance testing
- Configuration metadata saved with all results

### Inputs:
```
risk_score
goal_pressure
allocation
runway
savings_rate
```

### Output (API-facing)
```json
{
  "action": "increase_savings",
  "delta": 5,
  "allocation_shift": {
      "equity": +5,
      "cash": -5
  }
}
```

Note: the implementation currently shifts between `equity` and `debt` (not `cash`) for the allocation shift actions.
### Formalize
```python
env.step(action):
    apply savings change
    simulate returns
    update balances
    recompute agents
    return new_state, reward
```

---


### 6. Narrator (LLM)

#### 6.1 Purpose

Take all structured outputs and turn them into a human-readable report, with:

- Clear sections.
- 3–8 bullet summary.
- Short “what changed” paragraph.
- Strong disclaimer.

#### 6.2 Inputs

```python
class NarratorInput(TypedDict):
    profile: dict  # age, base_currency, risk_appetite
    risk: dict     # output from Risk Agent
    goals: list[dict]  # outputs from Goal Feasibility Agent
    allocation: dict   # outputs from Investment Agent
    strategy: dict
    previous_report: Optional[dict]
```

Backend builds this from DB models and agent outputs, plus the strategy output.

#### 6.3 Output Schema

```python
class NarratorOutput(TypedDict):
    summary_bullets: list[str]      # 3–8 items
    cashflow_section: str
    goals_section: str
    allocation_section: str
    changes_since_last: str         # 4–5 line paragraph
    disclaimer: str
    markdown_body: Optional[str]
```

#### 6.4 Prompt Design (High Level)

System prompt (conceptual):

- You are a calm financial planner.
- You are given structured quantitative inputs.
- Your job is to explain clearly, in simple language, what the numbers mean.
- You must not give specific security recommendations or tell the user to “buy/sell” anything.
- You must always remind that this is not financial advice.
- Output must be valid JSON with the specified schema and nothing else.

User prompt:

- Includes `NarratorInput` JSON.
- Asks the model to:
  - Summarize.
  - Describe cashflow and runway.
  - Analyze goals and feasibility.
  - Explain suggested asset-class allocation and trade-offs.
  - Compare against `previous_report` if present.

LLM call:

```python
def generate_prognosis_report(input_data: NarratorInput) -> NarratorOutput:
    ...
```

Implementation notes:

- The integration is in `backend/integrations/llm_client.py`.
- If `settings.llm_provider == "gemini"` and `settings.llm_api_key` is present, it uses `google.genai` and parses `response.text` as JSON.
- Otherwise it returns a deterministic mock report for MVP.

---

## Pipeline execution flow

```json
raw_user_data
   ↓
RiskAgent
GoalAgent
InvestmentAgent
   ↓
State Encoder
   ↓
StrategyAgent (RL)
   ↓
Narrator LLM
   ↓
Dashboard
```

Production endpoints:

- `POST /api/prognosis/refresh` generates and caches a new report (with rate limit + fallback to cached report).
- `GET /api/prognosis/current` returns the last cached report.

---

### 7. Testing and Validation

- Unit tests for:
  - Risk Agent calculations (burn rate, runway, capacity score).
  - Goal Agent statuses under different savings/targets.
  - Investment Agent allocations for different risk/macro scenarios.
- LLM contracts:
  - JSON schema validation of Narrator output.
  - Guardrails for common failure modes (e.g., missing keys, non-JSON responses).

RL-specific checks (optional):

- State vector length is always 5 and ordering never changes.
- Action mapping remains stable between training and inference.

This spec is sufficient to implement all ML/agent components for the MVP without prior chat context.
