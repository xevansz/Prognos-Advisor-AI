# Prognosis AI

A Multi-Agent System for Personalized Financial Planning & Robo-Advisory

**Version:** 1.1 | **Date:** February 2026 | **Domain:** FinTech / Artificial Intelligence

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for Prognosis AI, a web-based financial tracking and robo-advisory application. Unlike traditional robo-advisors that rely on static algorithms, Prognosis AI utilizes a Multi-Agent System (MAS) combined with Large Language Models (LLMs) to provide hyper-personalized, context-aware financial guidance.

### 1.2 Scope
The application serves as a **non-custodial**, globally-available financial tracker and planning assistant. Users manually log accounts and transactions to maintain data privacy and control. Over time, support for importing statements (e.g., PDF/CSV) may be added, but is **out of scope for the MVP**.

The core innovation lies in the **Prognosis Engine**, where distinct AI agents (Risk, Goal, Investment) and an LLM analyze user data to generate:

- A cohesive financial health report (cashflow, runway, goal feasibility).
- Asset allocation suggestions at the **asset-class level only** (e.g., cash vs equity vs debt), never specific tickers or products.

Throughout the product, Prognosis AI is positioned as an **educational and planning tool**, not regulated financial advice.

## 2. System Architecture

The system follows a modern 3-tier architecture with additional external services:

1. **Presentation Layer:** React (Vite) frontend with interactive dashboards.
2. **Application Layer:** FastAPI backend orchestrating the Multi-Agent logic and integrations.
3. **Data Layer:** PostgreSQL (Supabase recommended) for ACID-compliant transaction management.
4. **External Services (Phase 1 and beyond):**
   - Supabase Auth (email/password auth + JWT).
   - FX rate API for currency conversion (cached for multiple days).
   - Public market indicators API(s) to derive a simple “macro state”.
   - LLM provider (e.g., Google Gemini Flash / xAI) for the Narrator agent.

### NOTE (Implementation Alignment)

The current MVP implementation differs from the originally proposed stack in a few areas. This PRD retains the full product scope, but the overlapping architecture/stack details below reflect what is currently implemented in the repository.

## 3. Functional Requirements

### 3.1 Financial Management (The Ledger)

#### 3.1.1 Account Management

- The system shall allow users to create **manual accounts** categorized by type, for example:
  - Bank
  - Cash
  - Holdings / Investments (e.g., Stocks/Mutual Funds)
  - Crypto
  - Other
- Each account shall store:
  - Name
  - Type
  - Currency
  - Current balance (user-maintained, updated via transactions).
- Holdings / investment-type accounts are:
  - **Included** in AI agents’ calculations for risk and planning.
  - **Excluded** from certain high-level UI aggregates (e.g., “spend vs income” charts) where appropriate, to avoid mixing day-to-day liquidity with long-term investments.

#### 3.1.2 Transaction Logging

- The system shall record **single-entry** transactions representing:
  - Credits (income / money coming in).
  - Debits (expenses / money going out).
- Users must specify at minimum:
  - Label / Name (free text, e.g., “salary”, “rent”, “groceries”).
  - Date.
  - Amount.
  - Type (Debit or Credit).
  - Account (the account impacted).
  - Optional description.
  - Optional “recurring monthly” flag.
- The “label” effectively acts as a category signal (there is no rigid category taxonomy in MVP).
- **Automated Updates:** Upon logging a transaction, the system must automatically update the linked account balance in the database (atomic transaction).
- **Multi-currency support:**
  - Each transaction is stored in the currency of its account.
  - For reporting and AI agents, amounts are converted to the user’s **base currency** using cached FX rates.

#### 3.1.3 Recurring Transactions

- MVP: support **monthly recurring** transactions.
  - When creating a transaction, the user can mark it as “Recurring monthly”.
  - The system shall automatically create the next month’s instance on or around midnight of the due date.
- Weekly/yearly or more complex schedules are considered **post-MVP enhancements**.

#### 3.1.4 Portfolio & Cashflow Overview

- The system shall display a visual dashboard including at least:
  - **Total Net Worth** card (in user’s base currency), combining liquid assets and user-reported investment balances.
  - **Monthly Spending vs Income** chart (time series).
  - **Asset distribution** pie chart by account type or class (e.g., Bank, Cash, Holdings).
- Investments / holdings:
  - Are tracked at the level of “total amount in this account” (e.g., “₹60k in stocks”), not individual lots or tickers.
  - Are visible in the Accounts view, and used by the agents when computing risk, goals, and suggested allocations.

### 3.2 User Profile & Goals

#### 3.2.1 Profile Settings

- Each user profile shall include:
  - Email (required, for login/auth).
  - Age (required for risk and planning).
  - Optional display name (free text; not used in calculations).
  - Optional gender (may be removed later if not needed).
  - Base currency (e.g., INR, USD, EUR) for reporting and agents.
  - Subjective risk appetite:
    - Conservative
    - Moderate
    - Aggressive
- All financial data in dashboards and Prognosis reports shall be normalized to the user’s base currency using FX rates.

#### 3.2.2 Goal Definition

- Users shall define financial goals with parameters:
  - Goal Name.
  - Target Amount.
  - Target Time / Horizon (e.g., in months/years).
  - Priority (High / Medium / Low).
- Goals are generic (e.g., “Emergency Fund”, “Vacation”, “Debt Payoff”, “Education”); the system does not enforce specific goal types.
- Priority influences how the AI agents weigh each goal when recommending savings and allocations.

### 3.3 The Prognosis Engine (AI Core)

The **Prognosis Report** page is the central feature. It is generated **on-demand** when the user clicks the “Refresh Prognosis” button.

- In production, the backend may limit full re-computation to a maximum of **5 times per day per user**, and otherwise return a cached report.
- For MVP demos and investor pitches, this rate limiting can be disabled while keeping the logic in place.

The engine consists of three primary agents and a Narrator (LLM).

#### 3.3.1 Risk Agent (Logic-Based)

- **Inputs:**
  - Last 30–60 days of transaction history (credits/debits in base currency).
  - Total liquid assets (primarily Bank and Cash accounts; may include certain easily-sellable holdings).
- **Functions:**
  - Compute **Burn Rate** (average monthly spend).
  - Compute **Runway** (how many months until the liquid assets would reach zero, given current burn).
  - Derive a **Risk Capacity Score** between 0–100 (e.g., lower if runway is short).
- **Output:**
  - `burn_rate`.
  - `runway_months`.
  - `risk_capacity_score` (0–100).
  - Additional structured data for explanation.

#### 3.3.2 Goal Feasibility Agent (Math-Based)

- **Inputs:**
  - User goals (amount, time horizon, priority).
  - **Current monthly savings**, defined as:
    - Monthly savings = (sum of credits in period) − (sum of debits in period), ignoring investment returns.
- **Functions:**
  - Use basic financial math / TVM-style reasoning to estimate whether each goal is:
    - On Track.
    - At Risk.
    - Unrealistic.
- **Output:**
  - For each goal:
    - Status flag: On Track / At Risk / Unrealistic.
    - Key quantitative reasons (e.g., gap between required and actual savings).

#### 3.3.3 Investment Agent (Allocation Policy; RL-ready)

- **Inputs:**
  - Risk Capacity Score (from Risk Agent).
  - Stated Risk Appetite (Conservative / Moderate / Aggressive).
  - Aggregated goal statuses (from Goal Feasibility Agent).
  - Simplified **macro state**, derived from public indicators (e.g., bull/bear regime, high vs low rates).
- **Functions (MVP):**
  - Use a **rules-based or heuristic policy** to determine a recommended allocation across asset classes, such as:
    - Cash
    - Debt / Fixed Income
    - Equity
    - Possibly others (e.g., Gold, Crypto) as needed.
  - Respect constraints:
    - Never recommend specific tickers or products.
    - If user's appetite is Aggressive but capacity is low, produce **two plans**:
      - A recommended (safer) plan aligned with capacity.
      - An alternative plan aligned with the user's stated higher risk, clearly labeled as such.
- **RL Integration (Implemented):**
  - A DQN-based strategy agent is now implemented and can replace the heuristic policy.
  - The RL agent operates over a 5-dimensional state space and 5-action discrete action space.
  - Training environment includes realistic market regimes, income/expense shocks, and paper-faithful goal feasibility calculations.
  - Comprehensive evaluation pipeline with baseline comparisons is available.
  - See `docs/ml.md` for detailed RL specifications and recent improvements.

#### 3.3.4 Narrator (LLM)

- **Inputs:**
  - Structured JSON outputs from:
    - Risk Agent.
    - Goal Feasibility Agent.
    - Investment Agent.
  - Optionally, the last generated report for “what changed” comparisons.
- **Function:**
  - Synthesizes the technical data into a **human-readable “Prognosis Report”** in a calm, non-judgmental tone, always emphasizing uncertainty and the fact that this is **not financial advice**.
- **Output (JSON structure):**
  - `summary_bullets: string[]` (3–8 bullet points).
  - `cashflow_section: string`.
  - `goals_section: string`.
  - `allocation_section: string`.
  - `changes_since_last: string` (short paragraph).
  - `disclaimer: string`.
  - Optional `markdown_body: string` for a complete renderable report.

*Expected Outcome:* An AI-powered robo-advisory system that uses agent-based reasoning and (eventually) reinforcement learning to generate, explain, and continuously adapt personalized financial plans based on user goals, behavior, and market conditions, surfaced through simple, understandable visual dashboards.

## 4. Non-Functional Requirements

### 4.1 Performance

- **On-Demand Processing:** Prognosis Report generation (all agents + LLM call) shall typically not exceed **10 seconds** for a user with up to 10,000 transactions.
- **Caching:** The system shall store the last generated report in the database to allow instant page loads on subsequent visits until a “Refresh” is triggered.

### 4.2 Security & Privacy

- **Authentication:**
  - The MVP uses **Supabase-issued JWTs** to identify the user.
  - The backend extracts the `user_id` from the JWT subject (`sub`) to scope all queries.
  - **Current MVP behavior:** decodes token claims without signature verification.
  - **Production requirement:** verify JWT signatures using Supabase JWKS (and validate issuer/audience).
- **Data Isolation:**
  - All database queries must be scoped to the authenticated `user_id` to prevent data leakage between users.
- **Data Minimization:**
  - Only data necessary for planning and reporting is collected (e.g., age, email, base currency, risk appetite).
  - User’s chosen display name and gender are optional and not required for the AI logic.

### 4.3 Scalability

- The database schema shall be designed with proper indexing on `user_id`, `transaction_date`, and other key fields to handle **10,000+ transaction rows per user** without noticeable latency in common queries.
- The system shall support multi-currency calculations by caching FX rates from a free public API:
  - FX rates are refreshed at least every **3 days**.
  - For MVP, current spot rates can be used across all historical data.

### 4.4 Reliability & Rate Limiting

- The backend may enforce a limit of **up to 5 Prognosis Report refreshes per user per day** in production environments to control cost and load.
- When the limit is reached, the API will return the last cached report along with metadata (e.g., `last_generated_at`).

## 5. Technology Stack

| Component           | Technology                         | Reasoning                                                   |
| :---               | :---                               | :---                                                       |
| **Frontend**       | React + Vite + TypeScript          | Interactive dashboards with a fast dev/build toolchain.    |
| **UI/Charts**      | MUI + Radix UI + Recharts          | Component primitives + financial visualization.            |
| **Backend**        | Python (FastAPI)                   | High-performance async APIs and ML/AI integrations.        |
| **Database**       | PostgreSQL (Supabase recommended)  | Relational integrity for financial ledgers.                |
| **ORM/Migrations** | SQLAlchemy (async) + Alembic        | Async data access + schema migrations.                     |
| **Auth**           | Supabase Auth (JWT)                | Managed auth; backend scopes data by JWT subject.          |
| **LLM**            | Google Gemini (via `google-genai`) | Narrator agent; mock fallback when API key not set.        |
| **RL (future)**    | Custom / Stable-Baselines3         | For asset allocation policy learning.                      |
| **FX Data**        | Free public FX API                 | Multi-currency conversions to base currency.               |
| **Market Data**    | Public indicators API(s)           | Simple macro regime classification for Investment Agent.   |

## 6. Legal Positioning & Disclaimer

Prognosis AI is **not** a licensed financial advisor or broker. It is a **software tool** that helps users understand their own financial data and explore possible strategies.

**Core positioning:**

- The system provides **educational insights and planning suggestions**, not individualized financial advice.
- The application never recommends specific securities, products, or transactions (e.g., “buy/sell this stock”); it only suggests **asset-class level strategies**.
