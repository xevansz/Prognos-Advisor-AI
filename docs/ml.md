## ML / Agents Technical Specification (MVP)

### 1. Overview

The ML/agents layer for the MVP is **deterministic and rules-based**, designed to be:

- Simple and explainable.
- Implemented as pure Python modules callable from the FastAPI backend.
- **RL-ready**: interfaces are defined so that a learned policy can later replace the heuristic Investment Agent.

Components:

- Risk Agent (logic-based).
- Goal Feasibility Agent (math-based).
- Investment Agent (heuristic).
- RL Strategy generator.
- Narrator (LLM-based report generator).

---

### 2. Shared Data Structures (Conceptual)

These are conceptual; concrete types live in backend code.

```python
class AccountLike(TypedDict):
    id: str
    type: Literal['bank', 'cash', 'holdings', 'crypto', 'other']
    currency: str
    balance: float  # normalized to base currency where needed

class TransactionLike(TypedDict):
    id: str
    account_id: str
    date: date
    amount: float
    type: Literal['debit', 'credit']
    currency: str
    label: str

class GoalLike(TypedDict):
    id: str
    name: str
    target_amount: float
    target_date: date
    priority: Literal['high', 'medium', 'low']
```

The backend is responsible for **normalizing amounts to base currency** before passing them into the agents when required.

---

## pipeline:
`Data -> Agents -> State Vector -> RL policy -> Strategy -> LLM explanation`

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
- Recent transactions (last 60 days) in base currency.
- Liquid assets (sum of balances for `bank` and `cash` accounts; optionally some `holdings` if considered liquid).
- monthly_income

```python
def compute_risk_metrics(
    transactions: list[TransactionLike],
    liquid_accounts: list[AccountLike],
    lookback_days: int = 60
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
- goal_amount
- goal_deadline
- current_savings
- monthly_contribution
- expected_return

#### 4.3 Calculations (MVP)
For each goal:

1. Future Value:
  FV = current_savings*(1+r)^t + contribution * ((1+r)^t - 1)/r

2. compare:
  gap = goal_amount - FV

### Probability model (demo version)
We simulate uncertainity

Run monte carlo 500 times with random returns

Counts: success_rate = succesful_runs / total_runs

#### 4.4 Output
Per goal:

```json
{
  "goal_name": "Retirement",
  "projected_value": 1_200_000,
  "success_probability": 0.72,
  "status": "At Risk",
  "goal_pressure": 1 - success_probability
}
```

---

### 5. Macro State Classifier

#### 5.1 Purpose

Translate a small set of public indicators into a **discrete macro state** used by the Investment Agent.

#### 5.2 Inputs

- Simple indicators fetched from a public API (e.g., index level and moving average, basic rate/or yield).

Example conceptual input:

```python
class MarketIndicators(TypedDict):
    index_level: float
    index_200d_ma: float
    short_rate: float
    inflation_rate: float
```

---

### 5. Investment Agent (Heuristic, RL-Ready)

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
class GoalStatusLike(TypedDict):
    goal_id: str
    status: Literal['on_track', 'at_risk', 'unrealistic']
    priority_weight: float

def recommend_allocation(
    risk_score: int,             # 0–100
    risk_appetite: Literal['conservative', 'moderate', 'aggressive'],
    goal_time_horizon: int,
    goals_summary: list[GoalStatusLike],
    macro_state: str                      # 'bull', 'bear', 'recession', 'sideways'
) -> dict:
    ...
```

#### 6.7 Two-Plan Output (Capacity vs Appetite)
If risk appetite and capacity are in conflict (e.g., appetite = aggressive, capacity bucket = low):

- Compute:
  - `recommended` plan – bias by **capacity** (more conservative).
  - `aggressive_alternative` plan – reflect stated appetite within constraints.

If they are aligned:

- `aggressive_alternative` may equal `recommended` or be omitted.

#### 6.8 Output

```json
{
  "recommended": {
  total = equity + bonds + cash
  equity /= total
  bonds /= total
  cash /= total
  },
  "aggressive_alternative": {
  # same as recommended
  }
}
```

---

## Strategy Agent (RL wrapper)
what should next month

This agent consumes outputs from A/B/C

### RL (signals and outputs):
* savings rate adjustment
* debt payoff priority
* emergency reserve rule
* rebalancing frequency

### RL Environment:

state = [
  risk_score,
  goal_feasibility_score,
  current_equity_ratio,
  monthly_savings_rate,
  runway_months
]

### Actions:
0 = keep strategy
1 = increase savings by 5%
2 = reduce savings by 5%
3 = shift 10% to equity
4 = shift 10% to bonds

### Reward
reward =
    0.01 * net_worth_change
  - 2 if runway < 3 else 0
  + 5 if goal_on_track else -3

Each episode: 5 - 10 simulated years
Train episodes: 1000

### Inputs:
```
risk_score
goal_pressure
allocation
runway
savings_rate
```

### Output
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
    previous_report: Optional[dict]
```

Backend builds this from DB models and agent outputs.

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

---

## Pipeline execution flow
```
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

---

### 7. Testing and Validation

- Unit tests for:
  - Risk Agent calculations (burn rate, runway, capacity score).
  - Goal Agent statuses under different savings/targets.
  - Investment Agent allocations for different risk/macro scenarios.
- LLM contracts:
  - JSON schema validation of Narrator output.
  - Guardrails for common failure modes (e.g., missing keys, non-JSON responses).

This spec is sufficient to implement all ML/agent components for the MVP without prior chat context.

