## Prognosis AI – MVP Specification

**Timeline:** ~50 days  
**Goal:** Deliver a demo-ready, end-to-end version of Prognosis AI focused on simple, understandable financial tracking and AI-generated planning suggestions (not financial advice).

---

### 1. MVP Scope (In)

- **Authentication & User Profile**
  - Supabase Auth (email + password).
  - Basic profile: email, age (required), base currency, risk appetite, optional display name.

- **Accounts & Ledger**
  - Manual account creation with types: Bank, Cash, Holdings/Investments, Crypto, Other.
  - Per-account currency and balance.
  - Single-entry transactions:
    - Fields: label/name, date, amount, type (debit/credit), account, optional description.
    - Automatic balance updates in Postgres (atomic).
  - Monthly recurring transactions:
    - “Recurring monthly” flag on a transaction.
    - Auto-creation of next month’s transaction at midnight of due date.
  - Multi-currency support using base currency + FX API (current spot rates, cached every ~3 days).

- **Goals & Profile Settings**
  - Create/edit/delete goals with: name, target amount, horizon, priority (High/Med/Low).
  - Profile settings page for age, base currency, and risk appetite (Conservative/Moderate/Aggressive).

- **Prognosis Engine v1**
  - **Risk Agent (logic-based)**:
    - Inputs: last 30–60 days of transactions + liquid assets.
    - Outputs: burn rate, runway, risk capacity score (0–100).
  - **Goal Feasibility Agent (math-based)**:
    - Inputs: goals + current monthly savings (credits − debits, ignoring returns).
    - Outputs: per-goal status (On Track / At Risk / Unrealistic) with simple reasons.
  - **Investment Agent (heuristic, RL-ready)**:
    - Inputs: risk capacity, risk appetite, goal statuses, simple macro state.
    - Outputs: asset-class allocation suggestion (e.g., % Cash, % Debt, % Equity, etc.).
    - Special case: if appetite is high but capacity is low, return both a “recommended” safer plan and an “aggressive” alternative.
  - **Narrator (LLM)**:
    - Consumes structured outputs from the three agents.
    - Returns structured JSON (summary bullets, cashflow, goals, allocation, changes since last, disclaimer).
    - Tone: calm, clear, non-judgmental; always emphasizes “not financial advice”.
  - **Refresh flow**:
    - “Refresh Prognosis” button triggers recomputation + LLM call.
    - Last report cached in DB and reused for fast loads.
    - Rate limiting logic (max 5/day) implemented in backend but **disabled for MVP demos** via config/flag.

- **Dashboards & UI**
  - Simple Svelte/SvelteKit frontend following KISS:
    - **Overview page**:
      - Total Net Worth card (base currency).
      - Monthly Income vs Spending chart.
      - Asset distribution pie chart by account type/class.
    - **Accounts page**:
      - List of accounts with balances, including holdings/investments.
    - **Transactions page**:
      - List + create/edit transactions, including recurring flag.
    - **Goals page**:
      - List + create/edit goals, show per-goal basic status indicator.
    - **Prognosis Report page**:
      - Render Narrator JSON: summary bullets, sections, clear disclaimer.

---

### 2. MVP Scope (Out / Later Phases)

- Bank/broker integration, statement uploads (PDF/CSV) and auto-import.
- Double-entry accounting and advanced transfer modeling.
- Detailed portfolio tracking (per-security lots, tickers, performance).
- Advanced recurring schedules (weekly/yearly, custom rules, holidays, EOM logic).
- Historical FX per transaction date and highly accurate backdated valuations.
- Full RL-based Investment Agent training and deployment (beyond a small prototype).
- Rich audit tooling (full formula breakdown, step-by-step agent reasoning UI).
- Complex dashboards and power-user analytics (factor exposures, risk metrics, etc.).

---

### 3. Non-Functional MVP Targets

- **Performance**
  - End-to-end Prognosis Report generation typically < 10 seconds for up to 10k transactions.

- **Security & Privacy**
  - All endpoints protected via Supabase JWT.
  - All queries scoped to `user_id` for isolation.

- **Developer Experience**
  - Clear agent interfaces (inputs/outputs typed and documented) so RL and more advanced logic can be plugged in later without breaking the API.

---

### 4. Positioning (for MVP Demo)

- Prognosis AI is presented as:
  - A **global, non-custodial financial tracker and planning assistant**.
  - An AI-powered simulator that helps users **understand their situation and explore possible strategies**, not a source of regulated financial advice.
- The UI and copy consistently:
  - Avoid direct “buy/sell” recommendations.
  - Focus on education, clarity, and optional suggestions at the **asset-class level** only.

