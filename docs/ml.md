## ML / Agents Technical Specification (MVP)

### 1. Overview

The ML/agents layer for the MVP is **deterministic and rules-based**, designed to be:

- Simple and explainable.
- Implemented as pure Python modules callable from the FastAPI backend.
- **RL-ready**: interfaces are defined so that a learned policy can later replace the heuristic Investment Agent.

Components:

- Risk Agent (logic-based).
- Goal Feasibility Agent (math-based).
- Investment Agent (heuristic, RL-ready).
- Macro State classifier (from public indicators).
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

### 3. Risk Agent

#### 3.1 Purpose

Compute:

- Burn Rate (average monthly spending).
- Runway (months until liquid assets run out).
- Risk Capacity Score (0–100).

#### 3.2 Inputs

- Recent transactions (last 30–60 days) in base currency.
- Liquid assets (sum of balances for `bank` and `cash` accounts; optionally some `holdings` if considered liquid).

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
5. **Risk Capacity Score** (simple heuristic):
   - Map runway to a 0–100 scale, e.g.:
     - 0 months → score 0.
     - 12+ months → score 100.
     - Linear in between:
       - `score = clamp( (runway_months / 12) * 100, 0, 100 )`.

#### 3.4 Output

```json
{
  "burn_rate": 45000.0,
  "runway_months": 7.2,
  "risk_capacity_score": 60
}
```

---

### 4. Goal Feasibility Agent

#### 4.1 Purpose

Assess for each goal whether it is:

- On Track.
- At Risk.
- Unrealistic.

Based on current savings vs what would be required to hit the target by the target date.

#### 4.2 Inputs

- Goals list.
- Current **monthly savings** (scalar, base currency):
  - Monthly savings = sum(credits) − sum(debits) over a recent month, ignoring investment returns.

```python
def evaluate_goals(
    goals: list[GoalLike],
    monthly_savings: float,
    now: date
) -> list[dict]:
    ...
```

#### 4.3 Calculations (MVP)

For each goal:

1. **Time remaining**:
   - `months_remaining = max(1, months_between(now, goal.target_date))`.
2. **Required monthly saving**:
   - `required = goal.target_amount / months_remaining`.
   - MVP: ignore interest/inflation; later we can incorporate TVM.
3. **Feasibility status**:
   - Define thresholds, e.g.:
     - If `monthly_savings >= required * 0.9`:
       - `status = "on_track"`.
     - Else if `monthly_savings >= required * 0.5`:
       - `status = "at_risk"`.
     - Else:
       - `status = "unrealistic"`.
4. **Priority weighting** (for downstream use):
   - Compute a weight:
     - `high` → 1.0
     - `medium` → 0.7
     - `low` → 0.4

#### 4.4 Output

Per goal:

```json
{
  "goal_id": "uuid",
  "status": "on_track",
  "required_monthly_savings": 20000.0,
  "actual_monthly_savings": 21000.0,
  "priority": "high",
  "priority_weight": 1.0
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

#### 5.3 Classification (MVP Heuristic)

Possible states:

- `bull`
- `bear`
- `recession`
- `sideways`

Rules (example, to be refined):

- If `index_level > 1.05 * index_200d_ma` and `inflation_rate` moderate → `bull`.
- If `index_level < 0.95 * index_200d_ma` and `short_rate` high → `bear`.
- If `index_level` depressed + `short_rate` high + `inflation_rate` high → `recession`.
- Else → `sideways`.

Implementation:

```python
def classify_macro_state(indicators: MarketIndicators) -> str:
    ...
```

---

### 6. Investment Agent (Heuristic, RL-Ready)

#### 6.1 Purpose

Convert:

- Risk capacity (0–100).
- Stated risk appetite.
- Goal statuses and priority.
- Macro state.

Into a target **asset-class allocation**.

#### 6.2 Asset Classes (MVP)

- `cash`
- `debt`
- `equity`
- `other` (e.g., gold, crypto).

Allocations sum to 1.0.

#### 6.3 Inputs

```python
class GoalStatusLike(TypedDict):
    goal_id: str
    status: Literal['on_track', 'at_risk', 'unrealistic']
    priority_weight: float

def recommend_allocation(
    risk_capacity_score: int,             # 0–100
    risk_appetite: Literal['conservative', 'moderate', 'aggressive'],
    goals_summary: list[GoalStatusLike],
    macro_state: str                      # 'bull', 'bear', 'recession', 'sideways'
) -> dict:
    ...
```

#### 6.4 Base Policy (Ignoring Macro & Goals)

Define a **base allocation** per combination of risk appetite and capacity bucket.

Example buckets:

- Capacity low: 0–33.
- Medium: 34–66.
- High: 67–100.

For each [capacity_bucket, appetite], define base percentages:

- Conservative + low:
  - `cash=0.30, debt=0.50, equity=0.15, other=0.05`
- Conservative + high:
  - `cash=0.20, debt=0.55, equity=0.20, other=0.05`
- Moderate + medium:
  - `cash=0.15, debt=0.35, equity=0.45, other=0.05`
- Aggressive + high:
  - `cash=0.05, debt=0.20, equity=0.70, other=0.05`

Actual table to be implemented in code but documented as a set of presets.

#### 6.5 Adjustments from Macro State

Example adjustments:

- If `macro_state == "bear"`:
  - Reduce equity by 5–10 percentage points.
  - Reallocate to debt/cash.
- If `macro_state == "bull"`:
  - Increase equity by 5–10 points, reduce cash.
- If `macro_state == "recession"`:
  - Favor higher-quality debt and cash; cap equity.

MVP: simple additive adjustments with clamping to [0, 1] and renormalization.

#### 6.6 Goal-Based Tilt

Approximate:

- If many high-priority goals are `at_risk` or `unrealistic`, and time horizons are short:
  - Slightly tilt towards **more conservative** allocations (more cash/debt).
- For long-horizon goals that are mostly `on_track`:
  - Keep or modestly increase equity share depending on appetite/capacity.

Implementation detail:

- Compute a “goal stress score”:

```python
stress = sum(
  weight_for_status(gs.status) * gs.priority_weight
  for gs in goals_summary
)
```

Where `weight_for_status` could be:

- on_track → 0.0
- at_risk → 0.5
- unrealistic → 1.0

Then use thresholds on `stress` to nudge allocations more conservative.

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
    "cash": 0.15,
    "debt": 0.35,
    "equity": 0.45,
    "other": 0.05
  },
  "aggressive_alternative": {
    "cash": 0.05,
    "debt": 0.20,
    "equity": 0.70,
    "other": 0.05
  }
}
```

#### 6.9 RL-Ready Architecture

To prepare for RL:

- Define a **state vector** in a separate module:

```python
def build_state_vector(
    risk_capacity_score: int,
    risk_appetite: str,
    goals_summary: list[GoalStatusLike],
    macro_state: str
) -> np.ndarray:
    ...
```

- Define an **action vector** as `[cash, debt, equity, other]`.
- The heuristic policy then becomes “the default implementation”; an RL policy can later implement:

```python
def rl_policy(state: np.ndarray) -> np.ndarray:
    ...
```

Without changing how the rest of the system calls the Investment Agent.

---

### 7. Narrator (LLM)

#### 7.1 Purpose

Take all structured outputs and turn them into a human-readable report, with:

- Clear sections.
- 3–8 bullet summary.
- Short “what changed” paragraph.
- Strong disclaimer.

#### 7.2 Inputs

```python
class NarratorInput(TypedDict):
    profile: dict  # age, base_currency, risk_appetite
    risk: dict     # output from Risk Agent
    goals: list[dict]  # outputs from Goal Feasibility Agent
    allocation: dict   # outputs from Investment Agent
    previous_report: Optional[dict]
```

Backend builds this from DB models and agent outputs.

#### 7.3 Output Schema

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

#### 7.4 Prompt Design (High Level)

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

### 8. Testing and Validation

- Unit tests for:
  - Risk Agent calculations (burn rate, runway, capacity score).
  - Goal Agent statuses under different savings/targets.
  - Investment Agent allocations for different risk/macro scenarios.
- LLM contracts:
  - JSON schema validation of Narrator output.
  - Guardrails for common failure modes (e.g., missing keys, non-JSON responses).

This spec is sufficient to implement all ML/agent components for the MVP without prior chat context.

