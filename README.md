# Prognosis AI

**A Multi-Agent System for Personalized Financial Planning & Robo-Advisory**

**Version:** 1.0 | **Date:** January 2026 | **Domain:** FinTech / Artificial Intelligence

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for Prognosis AI, a web-based financial advisory application. Unlike traditional robo-advisors that rely on static algorithms, Prognosis AI utilizes a Multi-Agent System (MAS) combined with Large Language Models (LLMs) to provide hyper-personalized, context-aware financial guidance.

### 1.2 Scope
The application serves as a non-custodial financial tracker and advisor. It allows users to manually log assets and transactions to maintain data privacy. The core innovation lies in the "Prognosis Engine," where distinct AI agents (Risk, Goal, Investment) analyze user data to generate a cohesive financial health report and asset allocation strategy.

## 2. System Architecture

The system follows a modern 3-tier architecture:
1. **Presentation Layer:** React-based frontend with interactive dashboards.
2. **Application Layer:** FastAPI backend orchestrating the Multi-Agent Logic.
3. **Data Layer:** PostgreSQL database for ACID-compliant transaction management.

## 3. Functional Requirements

### 3.1 Financial Management (The Ledger)

* **3.1.1 Account Management:**
    * The system shall allow users to create manual accounts categorized by type: Bank, Cash, Holdings (Stocks/Mutual Funds), Crypto, Other.
    * The system shall maintain a current balance for each account.
* **3.1.2 Transaction Logging:**
    * The system shall record Credits (Income) and Debits (Expenses).
    * Users must specify: Date, Amount, Category, Source Account, Description.
    * **Automated Updates:** Upon logging a transaction, the system must automatically update the linked Account balance in the database (Atomic Transaction).
* **3.1.3 Portfolio Overview:**
    * The system shall display a visual dashboard including:
        * Total Net Worth card.
        * Monthly Spending vs Income chart.
        * Asset distribution pie chart (e.g., 40% Bank, 60% Holdings).

### 3.2 User Profile & Goals

* **3.2.1 Goal Definition:**
    * Users shall define financial goals with parameters: Goal Name, Target Amount, Target Date, Priority (High/Med/Low).
* **3.2.2 Profile Settings:**
    * Users shall input demographic data (Age, Gender) and subjective Risk Appetite (Conservative, Moderate, Aggressive) to calibrate the AI agents.

### 3.3 The Prognosis Engine (AI Core)
The "Prognosis Report" page is the central feature. It is on-demand, triggered only when the user clicks the "Refresh Prognosis" button.

* **3.3.1 The Risk Agent (Logic-Based):**
    * Input: Last 30-60 days of transaction history + Total Liquid Assets.
    * Function: Calculates "Burn Rate" (Avg. Monthly Spend) and "Runway" (Months until insolvency).
    * Output: Risk Capacity Score (0-100).
* **3.3.2 The Goal Feasibility Agent (Math-Based):**
    * Input: User Goals + Current Monthly Savings.
    * Function: Uses Time Value of Money (TVM) formulas to calculate probability of success.
    * Output: Status flag (On Track, At Risk, Unrealistic).
* **3.3.3 The Investment Agent (RL):**
    * Input: User Risk Score + Current Market State (Macro-trends).
    * Function: Determines the optimal Asset Allocation mix.
    * Constraint: The agent shall not recommend specific tickers (e.g., "Buy AAPL") but rather asset classes (e.g., "Increase Equity exposure to 60%, Reduce Cash").
* **3.3.4 The Narrator (LLM - Gemini Flash):**
    * Input: Structured JSON outputs from Agents A, B, and C.
    * Function: Synthesizes technical data into a human-readable "Prognosis Report."
    * Output: A structured textual report explaining why the goal is at risk and justifying the recommended asset allocation.

## 4. Non-Functional Requirements

### 4.1 Performance
* **On-Demand Processing:** The Prognosis Report generation shall not exceed 10 seconds.
* **Caching:** The system shall store the last generated report in the database to allow instant page loads on subsequent visits until a "Refresh" is triggered.

### 4.2 Security
* **Authentication:** Access shall be secured via JWT (JSON Web Tokens).
* **Data Isolation:** All database queries must be scoped to the authenticated `user_id` to prevent data leakage between users.

### 4.3 Scalability
* The database schema shall be designed with proper indexing on `transaction_date` and `user_id` to handle 10,000+ transaction rows per user without latency.

## 5. Technology Stack

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Frontend** | React.js + Recharts | Responsive UI and financial visualization. |
| **Backend** | Python (FastAPI) | High-performance async support for ML inference. |
| **Database** | PostgreSQL | Relational integrity for financial ledgers. |
| **LLM** | Google Gemini Flash | Cost-effective, large context window for history analysis. |
| **RL Model** | Custom / Stable-Baselines3 | For Asset Allocation optimization logic. |
