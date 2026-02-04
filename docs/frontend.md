## Frontend Technical Specification (MVP)

### 1. Overview

- **Framework**: SvelteKit.
- **Language**: TypeScript.
- **Styling**: Tailwind CSS (or utility-first equivalent) for rapid, consistent UI.
- **Charts**: Any mature Svelte-compatible charting library (e.g., ApexCharts wrapper); details can be swapped if the API is similar.
- **API Access**: Typed API client using `fetch` from SvelteKit endpoints or directly to FastAPI (`/api/...`), with JWT from Supabase.

Primary goals:

- Simple, understandable UI (KISS).
- Clear separation of **pages** (routes) and **shared components** (cards, charts, forms).

---

### 2. Routing Structure

Assuming SvelteKit file-based routing under `src/routes`:

- `/` – redirect or landing page:
  - If not authenticated → redirect to `/auth/login`.
  - If authenticated → redirect to `/overview`.

- `/auth/login`
  - Email/password login using Supabase Auth client.

- `/auth/register`
  - Email/password signup.

- `/auth/callback` (optional)
  - For handling password reset / email confirmations if needed.

- `/onboarding`
  - First-time setup flow:
    - Age, base currency, risk appetite.
    - Optionally set display name.

- `/overview`
  - Main dashboard with:
    - Net Worth card.
    - Monthly Income vs Spending chart.
    - Asset distribution pie chart.

- `/accounts`
  - List of accounts with balances.
  - “Create account” modal/form.
  - Link to view transactions filtered by account (`/transactions?account_id=...`).

- `/transactions`
  - Filterable list of transactions.
  - Create/edit transaction form (inline modal or separate page).

- `/goals`
  - List of goals.
  - Create/edit goal form.

- `/prognosis`
  - Shows last Prognosis Report.
  - “Refresh Prognosis” button triggers API call.

- `/settings`
  - Change profile settings:
    - Display name, base currency, risk appetite.
  - View legal disclaimer summary and link to full text.

---

### 3. Global State and Auth Handling

#### 3.1 Supabase Integration

- Initialize Supabase client in a shared module (e.g., `src/lib/supabaseClient.ts`).
- Use Supabase session to:
  - Store JWT.
  - Keep user logged in across reloads.

#### 3.2 Session Management

- SvelteKit `load` functions on protected pages:
  - Check for Supabase session.
  - If no session → redirect to `/auth/login`.

- For API calls:
  - Attach `Authorization: Bearer <access_token>` header to all `/api/...` requests.

---

### 4. Types and API Client

Define TypeScript interfaces mirroring backend DTOs.

#### 4.1 Core Types

```ts
export type RiskAppetite = 'conservative' | 'moderate' | 'aggressive';

export interface Profile {
  age: number;
  display_name?: string;
  gender?: string;
  base_currency: string;
  risk_appetite: RiskAppetite;
}

export type AccountType = 'bank' | 'cash' | 'holdings' | 'crypto' | 'other';

export interface Account {
  id: string;
  name: string;
  type: AccountType;
  currency: string;
  balance: number;
}

export type TransactionType = 'debit' | 'credit';

export interface Transaction {
  id: string;
  account_id: string;
  label: string;
  description?: string;
  date: string; // ISO date
  amount: number;
  type: TransactionType;
  currency: string;
  is_recurring: boolean;
}

export type GoalPriority = 'high' | 'medium' | 'low';

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  target_currency: string;
  target_date: string;
  priority: GoalPriority;
}

export interface PrognosisReport {
  summary_bullets: string[];
  cashflow_section: string;
  goals_section: string;
  allocation_section: string;
  changes_since_last: string;
  disclaimer: string;
  markdown_body?: string;
  generated_at?: string;
}
```

#### 4.2 API Client Module

Create a `src/lib/api.ts` module that wraps HTTP calls:

```ts
async function apiGet<T>(path: string): Promise<T> { ... }
async function apiPost<TReq, TRes>(path: string, body: TReq): Promise<TRes> { ... }
async function apiPut<TReq, TRes>(path: string, body: TReq): Promise<TRes> { ... }
async function apiDelete<TRes>(path: string): Promise<TRes> { ... }
```

Each function:

- Prepends `/api` to path.
- Attaches `Authorization` header.
- Handles JSON encoding/decoding and basic error handling.

---

### 5. Page-Level Behavior

#### 5.1 Onboarding (`/onboarding`)

- Flow:
  1. Fetch existing profile (`GET /api/profile`).
  2. If profile complete → redirect to `/overview`.
  3. Otherwise render form:
     - Age (number).
     - Base currency (dropdown).
     - Risk appetite (radio buttons).
     - Optional display name.
  4. On submit → `PUT /api/profile` then redirect to `/overview`.

#### 5.2 Overview (`/overview`)

- Data:
  - Fetch accounts (`GET /api/accounts`).
  - Fetch transactions for the last N months (`GET /api/transactions?...`).
- Calculations on frontend (or fetch from a summary endpoint if later added):
  - Net worth = sum of account balances converted to base currency (backend may already provide normalized balances).
  - Monthly income vs spending by month.
  - Asset distribution by account type.
- UI:
  - Net Worth card with base currency symbol.
  - Line/bar chart for Income vs Spending.
  - Pie/donut chart for asset distribution.

#### 5.3 Accounts (`/accounts`)

- List:
  - Table/cards of accounts: name, type, currency, balance.
  - Button “Add Account” → opens modal.
- Create:
  - Form fields: name, type, currency, optional initial balance.
  - Call `POST /api/accounts`.

#### 5.4 Transactions (`/transactions`)

- Filters:
  - Account selector (dropdown).
  - Date range.
- List:
  - Table of transactions: date, label, account, type, amount, is_recurring indicator.
  - Actions: edit, delete.
- Create/Edit:
  - Form fields: account, label, description, date, amount, type, currency (read-only or account-based), `is_recurring` checkbox.
  - Create: `POST /api/transactions`.
  - Edit: `PUT /api/transactions/{id}`.

#### 5.5 Goals (`/goals`)

- List:
  - Card per goal: name, target amount, target date, priority.
  - Basic status badge if prognosis data is available (e.g., On Track / At Risk / Unrealistic).
- Create/Edit:
  - Form fields: name, target amount, target date, priority.
  - API: `POST /api/goals`, `PUT /api/goals/{id}`, `DELETE /api/goals/{id}`.

#### 5.6 Prognosis (`/prognosis`)

- On load:
  - Call `GET /api/prognosis/current`.
  - If none → show empty state with “Generate your first Prognosis”.
- Refresh:
  - Clicking “Refresh Prognosis” calls `POST /api/prognosis/refresh`.
  - Show loading state and handle possible rate-limit messages (if backend flag ever enabled).
- Display:
  - Render `summary_bullets` as bullets.
  - Render text sections as paragraphs (or markdown if `markdown_body` provided).
  - Always show disclaimer at bottom.

#### 5.7 Settings (`/settings`)

- Profile section:
  - Edit age, base currency, risk appetite, display name.
  - Bound to `GET/PUT /api/profile`.
- Legal section:
  - Show short summary + link to full disclaimer (e.g., from `PRD` or separate static page).

---

### 6. Components

Create a small set of reusable components under `src/lib/components`:

- `Card.svelte`
- `Button.svelte`
- `Input.svelte`, `Select.svelte`, `Toggle.svelte`
- `ChartLine.svelte`, `ChartPie.svelte` (wrapping the chart library)
- `PageHeader.svelte` (title + optional actions)
- `Loader.svelte` (spinner or skeleton)
- `ErrorBanner.svelte`

These components should be generic and used across pages for a consistent look.

---

### 7. Styling and UX Guidelines

- **KISS**:
  - Avoid hidden advanced options; keep forms and dashboards straightforward.
  - Use plain language labels (e.g., “Money coming in” instead of only “Credits” where appropriate).
- **Consistency**:
  - Same color coding for debits vs credits across the app.
  - Same chart color palette on all pages.
- **Responsiveness**:
  - Layout should work on desktop and tablet; mobile support is a plus but not mandatory for MVP.

---

### 8. Error Handling & Loading States

- All pages must:
  - Show a loading state while data is being fetched.
  - Show a clear, friendly error if API calls fail.
  - Allow retry of failed fetches.

---

### 9. Developer Experience

- Use TypeScript types for all API responses and ensure compile-time checking.
- Keep page `load` functions slim; move logic into `lib/api` and `lib/utils` helpers where possible.

This spec should be sufficient to implement the entire MVP frontend without the original chat history.

