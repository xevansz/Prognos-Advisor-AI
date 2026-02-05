## Backend Technical Specification (MVP)

### 1. Overview

- **Framework**: FastAPI (Python 3.11+).
- **DB layer**: Supabase Cloud + SQLAlchemy when needed.
- **Auth**: Supabase Auth – backend trusts Supabase JWTs and uses `user_id` claim for scoping.
- **Architecture**: layered into `api` (routers), `services` (business logic), `models/schemas` (ORM + Pydantic), `integrations` (FX, market, LLM), and `core` (config, security, logging).

All endpoints are **per-user** and must scope queries by `user_id`.

---

### 2. Data Model (DB Schema)

#### 2.1 Users (shadow table)

The source of truth for auth is Supabase; backend may maintain a minimal shadow table.

- `users`
  - `id` (UUID, PK) – matches Supabase `user.id`.
  - `email` (text, unique).
  - `created_at` (timestamptz, default now).

#### 2.2 Profile

- `profiles`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, unique, indexed).
  - `age` (int, not null).
  - `display_name` (text, nullable).
  - `gender` (text, nullable).
  - `base_currency` (varchar(3), not null, e.g. `INR`, `USD`).
  - `risk_appetite` (enum: `conservative`, `moderate`, `aggressive`).
  - `created_at` (timestamptz).
  - `updated_at` (timestamptz).

#### 2.3 Accounts

- `accounts`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, indexed).
  - `name` (text, not null).
  - `type` (enum: `bank`, `cash`, `holdings`, `crypto`, `other`).
  - `currency` (varchar(3), not null).
  - `balance` (numeric(18, 4), not null, default 0).
  - `created_at` (timestamptz).
  - `updated_at` (timestamptz).

#### 2.4 Transactions

- `transactions`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, indexed).
  - `account_id` (UUID, FK → `accounts.id`, indexed).
  - `label` (text, not null) – user-provided name (“rent”, “salary”).
  - `description` (text, nullable).
  - `date` (date, not null, indexed).
  - `amount` (numeric(18, 4), not null).
  - `type` (enum: `debit`, `credit`).
  - `currency` (varchar(3), not null, defaults to account currency).
  - `is_recurring` (bool, default false).
  - `recurrence_rule_id` (UUID, FK → `recurrence_rules.id`, nullable).
  - `created_at` (timestamptz).
  - `updated_at` (timestamptz).

#### 2.5 Recurrence Rules (MVP: Monthly Only)

- `recurrence_rules`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, indexed).
  - `frequency` (enum: `monthly`).
  - `day_of_month` (int, nullable; if null, use original transaction’s day).
  - `start_date` (date, not null).
  - `end_date` (date, nullable).
  - `active` (bool, default true).
  - `created_at` (timestamptz).
  - `updated_at` (timestamptz).

#### 2.6 Goals

- `goals`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, indexed).
  - `name` (text, not null).
  - `target_amount` (numeric(18, 4), not null).
  - `target_currency` (varchar(3), not null, usually base currency).
  - `target_date` (date, not null).
  - `priority` (enum: `high`, `medium`, `low`).
  - `created_at` (timestamptz).
  - `updated_at` (timestamptz).

#### 2.7 FX Rates Cache

- `fx_rates`
  - `id` (UUID, PK).
  - `base_currency` (varchar(3), not null).
  - `rates` (jsonb, not null) – map of `currency_code` → numeric rate.
  - `fetched_at` (timestamptz, indexed).

Only the most recent row per base or global base is used; refresh at most every 3 days.

#### 2.8 Prognosis Reports & Rate Limiting

- `prognosis_reports`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, unique or indexed).
  - `report_json` (jsonb, not null) – full Narrator JSON output.
  - `inputs_snapshot` (jsonb, not null) – snapshot of inputs (aggregated balances, goals, macro state, etc.).
  - `generated_at` (timestamptz, indexed).

- `prognosis_usage`
  - `id` (UUID, PK).
  - `user_id` (UUID, FK → `users.id`, unique).
  - `date` (date, not null).
  - `count` (int, not null).
  - Unique constraint on (`user_id`, `date`).

---

### 3. API Design (FastAPI Routers)

All endpoints are prefixed with `/api` and require a valid Supabase JWT. The backend includes a dependency that:

1. Validates JWT signature and issuer.
2. Extracts `user_id`.
3. Injects `current_user` (or at least `user_id`) into request scope.

Error responses use a standard shape:

```json
{
  "detail": "Human-readable message",
  "code": "ERROR_CODE"
}
```

#### 3.1 Health

- `GET /api/health`
  - Returns `{ "status": "ok" }` for monitoring.

#### 3.2 Profile

- `GET /api/profile`
  - Returns profile for current user (creates a default record on first access if not present).

- `PUT /api/profile`
  - Body: `{ age, display_name?, gender?, base_currency, risk_appetite }`.
  - Upserts profile for current user.

#### 3.3 Accounts

- `GET /api/accounts`
  - Returns list of all accounts for `user_id`.

- `POST /api/accounts`
  - Body: `{ name, type, currency, initial_balance? }`.
  - Creates account; if `initial_balance` provided, sets `balance` and optionally creates a synthetic initial transaction (MVP may skip synthetic tx and just set balance).

- `GET /api/accounts/{account_id}`
  - Returns account details if owned by user.

- `PUT /api/accounts/{account_id}`
  - Body: `{ name?, type?, currency? }`.
  - Does not directly change `balance`; balances are driven by transactions or explicit admin-adjust endpoints (MVP can keep it simple: manual balance edits via a dedicated endpoint if needed).

- `DELETE /api/accounts/{account_id}`
  - Soft or hard delete; MVP can hard delete if no referential issues.

#### 3.4 Transactions

- `GET /api/transactions`
  - Query params: `account_id?`, `from_date?`, `to_date?`, pagination (`limit`, `offset`).
  - Returns paginated list of transactions for user.

- `POST /api/transactions`
  - Body:
    - `account_id`
    - `label`
    - `description?`
    - `date`
    - `amount`
    - `type` (`debit`/`credit`)
    - `currency?` (defaults to account currency)
    - `is_recurring?` (bool, default false)
  - Behavior:
    - Creates transaction in a DB transaction.
    - Updates account `balance`:
      - If `type == credit`: `balance += amount_converted_to_account_currency`.
      - If `type == debit`: `balance -= amount_converted_to_account_currency`.
    - If `is_recurring`:
      - Creates corresponding `recurrence_rules` row.
      - Links transaction via `recurrence_rule_id`.

- `PUT /api/transactions/{transaction_id}`
  - Allows editing date, label, description, amount, type, and possibly account.
  - Must adjust `accounts.balance` accordingly in a transaction (revert old effect, apply new).

- `DELETE /api/transactions/{transaction_id}`
  - Reverts its effect on `accounts.balance` before deletion (or marks as cancelled and compensates).

#### 3.5 Recurring Transactions Scheduler (Backend Job)

Not an HTTP endpoint; implemented as a scheduled task (cron, Celery beat, or simple startup task with sleep loop for MVP).

Logic (daily at e.g. 00:05):

1. For each active `recurrence_rules` with `frequency = monthly`:
   - Determine the **next due date**.
   - If due date is **today** and there is no generated transaction for this rule and date:
     - Clone a transaction skeleton (amount, label, account, type, description).
     - Insert new `transactions` row with `date = today`.
     - Update `accounts.balance` appropriately.

The initial “template” for a rule can be taken from the first transaction that created it.

#### 3.6 Goals

- `GET /api/goals`
  - Returns all goals for current user.

- `POST /api/goals`
  - Body: `{ name, target_amount, target_currency?, target_date, priority }`.
  - If `target_currency` omitted, defaults to user’s base currency.

- `PUT /api/goals/{goal_id}`
  - Edit any mutable fields.

- `DELETE /api/goals/{goal_id}`
  - Delete goal for user.

#### 3.7 FX Service

- `GET /api/fx/rates`
  - Optional: for debugging / UI.
  - Returns current cached FX rates.

Internal service:

- `fx_service.get_rate(from_currency, to_currency)`:
  - If cached rates are older than 3 days, fetch from external FX API and store in `fx_rates`.
  - Returns a numeric multiplier for conversion.

All financial logic that needs normalization to base currency should use this service.

#### 3.8 Macro State Service

Internal-only module:

- `macro_service.get_macro_state() -> str`:
  - Fetches a small set of indicators from a public API (e.g., index price vs MA, rates).
  - Classifies into discrete states: e.g., `bull`, `bear`, `recession`, `sideways`.
  - For MVP, classification can be a simple heuristic with a small number of states.

#### 3.9 Prognosis Engine Endpoints

- `POST /api/prognosis/refresh`
  - Body: none (uses current user data).
  - Flow:
    1. Check rate limit (if enabled via config flag):
       - Look up `prognosis_usage` for `user_id` and today.
       - If `count >= 5`, return last cached report with `429` or `200` plus a flag `rate_limited: true`.
    2. Load inputs:
       - Profile (age, base currency, risk appetite).
       - Accounts and balances.
       - Transactions (last 30–60 days for risk, and last full month for savings).
       - Goals.
       - FX rates and macro state.
    3. Call Risk Agent, Goal Feasibility Agent, Investment Agent (Python functions/services).
    4. Build a structured input JSON for Narrator.
    5. Call LLM integration (Narrator) to get report JSON.
    6. Persist:
       - Upsert `prognosis_reports` for user with `report_json` and `inputs_snapshot`.
       - Update/increment `prognosis_usage`.
    7. Return `report_json` plus metadata (e.g., `generated_at`).

- `GET /api/prognosis/current`
  - Returns last cached report for user or 404 if none.

#### 3.10 Config & Feature Flags

Backend should have a configuration mechanism (env-based) for:

- `PROGNOSIS_RATE_LIMIT_ENABLED` (bool; false for MVP demos).
- External API keys (FX, market data, LLM).
- LLM provider selection and model name.

---

### 4. Integrations

#### 4.1 Supabase Auth

- The backend will not manage passwords; it will:
  - Accept JWTs from the frontend in `Authorization: Bearer <token>`.
  - Verify JWT using Supabase-provided public key.
  - Extract `sub` or `user_id` claim to link to internal `users` table.
  - Optionally, create a `users` row on first ever request if not present.

#### 4.2 FX API

- A simple client module wrapping a free FX API.
- Functions:
  - `fetch_latest_rates(base_currency: str) -> dict[currency_code, rate]`.

#### 4.3 Market Indicators API

- Client module to fetch:
  - A few broad indicators needed for `macro_service`.
  - MVP can use a single global index (e.g., S&P 500 or equivalent) plus basic rate info.

#### 4.4 LLM Provider

- Client module for Narrator:
  - `generate_prognosis_report(input_json: dict) -> dict` (returns Narrator schema).
  - Handles:
    - Prompt construction (system + user).
    - Retry on transient failures.
    - Basic logging/tracing (without logging sensitive PII).

---

### 5. Agents (Backend Interfaces)

These are pure-Python services imported by the prognosis router.

#### 5.1 Risk Agent

- Function signature:

```python
def compute_risk_metrics(
    transactions: list[TransactionLike],
    liquid_accounts: list[AccountLike],
    base_currency: str,
) -> dict:
    ...
```

- Output (example):

```json
{
  "burn_rate": 45000.0,
  "runway_months": 7.2,
  "risk_capacity_score": 62
}
```

#### 5.2 Goal Feasibility Agent

- Function signature:

```python
def evaluate_goals(
    goals: list[GoalLike],
    monthly_savings: float,
    base_currency: str
) -> list[dict]:
    ...
```

- Per-goal output:

```json
{
  "goal_id": "...",
  "status": "on_track | at_risk | unrealistic",
  "required_monthly_savings": 20000.0,
  "actual_monthly_savings": 15000.0
}
```

#### 5.3 Investment Agent (Heuristic)

- Function signature:

```python
def recommend_allocation(
    risk_capacity_score: int,
    risk_appetite: str,
    goals_summary: list[GoalStatusLike],
    macro_state: str
) -> dict:
    ...
```

- Output example:

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

#### 5.4 Narrator Input/Output Types

- Narrator input:

```json
{
  "profile": { "age": 28, "base_currency": "INR", "risk_appetite": "moderate" },
  "risk": { ... },
  "goals": [ ... ],
  "allocation": { ... },
  "previous_report": { ... } // optional
}
```

- Narrator output:

```json
{
  "summary_bullets": ["...", "..."],
  "cashflow_section": "...",
  "goals_section": "...",
  "allocation_section": "...",
  "changes_since_last": "...",
  "disclaimer": "...",
  "markdown_body": "..." 
}
```

---

### 6. Logging, Monitoring, and Errors

- Centralized logging with:
  - Request ID per API call.
  - Warnings on failed external calls (FX, market, LLM).
- Graceful degradation:
  - If FX API fails, use last known rates; if none exist, return 503 for prognosis.
  - If LLM call fails, return a structured error and **do not** cache a partial report.

This spec should be sufficient to implement the entire MVP backend without our chat history.

