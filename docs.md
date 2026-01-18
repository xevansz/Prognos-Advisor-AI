## What This System Does

### User Perspective

1. User enters basic financial details

   * Income
   * Expenses
   * Age
   * Risk preference (Low / Medium / High)
   * Financial goals (short-term & long-term)

2. The system:

   * Evaluates the user's risk profile
   * Prioritizes goals based on time horizon
   * Generates an asset allocation plan (Equity / Debt / Cash)

3. The plan is:

   * Displayed visually using charts
   * Explained in natural language

4. When inputs change (e.g., expenses increase or a new goal is added):

   * The system recalculates and updates the plan dynamically

---

## Core Features

### 1. Financial Data Input

* Simple web form for collecting user financial information
* Input validation and consistency checks

### 2. Risk Profiling

* Rule-based classification into Low / Medium / High risk
* Uses factors like age, expenses, and stated preference

### 3. Goal-Based Planning

* Supports short-term, medium-term, and long-term goals
* Goals influence asset allocation and savings strategy

### 4. Plan Generation

* Generates a recommended asset allocation
* Calculates suggested monthly investment amount

### 5. Dynamic Adaptation

* Any change in user inputs triggers plan recalculation
* Simulates real-life financial planning adjustments

### 6. Explainability

* The system explains *why* a particular plan was chosen
* Focus on transparency and user understanding

### 7. Visual Dashboards

* Asset allocation pie chart
* Goal progress indicators
* Simulated portfolio growth over time

---

## AI & Intelligence Components

### Agent-Based Reasoning

The system is logically divided into three reasoning components:

* **Risk Agent** – evaluates user risk tolerance
* **Goal Agent** – prioritizes goals by importance and timeline
* **Investment Agent** – determines feasible asset allocation

These agents may be implemented using rules and heuristics rather than autonomous AI agents.

### Reinforcement Learning

* Used to demonstrate optimization of asset allocation
* Operates in a **simulated environment**
* Focuses on goal satisfaction and stability, not market prediction

### Explainable AI

* Generates human-readable explanations
* Converts numeric decisions into understandable reasoning

---

## Technology Stack (Planned)

### Backend

* Python
* FastAPI
* NumPy / Pandas
* Pydantic

### AI / Logic

* Rule-based financial logic
* lightweight reinforcement learning
* LLM-based explanation generation

### Frontend

* React (or simple JavaScript frontend) or Svelte or whatevers light.
* Charting library (Chart.js / Recharts / Plotly)

### Data

* need to research. we need to find portfolio dataset in kaggle.

---

## Scope

### Included

* Financial planning logic
* Goal-based recommendations
* Adaptive behavior
* Visual explanations

### Not Included

* Real-time stock data
* Trading or brokerage integration
* Tax filing or compliance logic
* Market prediction or forecasting

## Disclaimer

what should we claimer about?? hmm...

**Disclaimer:** 
* *Artificial Intelligence models can make mistakes.* 

* Any financial suggestions or insights provided by the application or its AI advisors are purely informational and non-binding.

* All decisions made based on such information are entirely at the user’s own discretion, and the advice provided cannot be relied upon as legal, financial, or professional counsel, nor can it be challenged in a court of law.

* The author(s) of the application make no representations, warranties, or guarantees of any kind, express or implied, including but not limited to warranties of accuracy, reliability, merchantability, or fitness for a particular purpose, and shall not be held liable for any loss, damage, or liability arising from the use of the application.

>    7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.


* Please check the licensing information provided here: [LICENSE](./LICENSE)

## System design

User → Frontend → Backend API → Planning Logic → Dashboard

* user
 - login/Auth
 - enters financial data
 - Change inputs and see updates

* frontend
Screen 1: Input Form
          Income
          Expenses
          Age
          Risk preference (dropdown)
          Goals (simple list)

Screen 2: Dashboard
          Asset allocation pie chart
          Goal progress bars
          Explanation text
          growth line chart

* Frontend responsibilities
Input validation (basic)
API calls
Rendering charts

* Backend

Receive user data
Call planning logic
Return results to frontend

only 1 api for now

* planning logic

- Risk Module

Input:
Age
Expenses
Risk preference

Output:
Risk category: Low / Medium / High

How it works:
Rule-based logic

Example:
Young + low expenses → higher risk allowed

High expenses → lower risk

- Goal Module

Input:
List of goals
Time horizon

Output:
Goal priorities
Required savings estimate (rough)

How it works:
Short-term goals → safer assets
Long-term goals → growth assets
No probability math needed yet.

- Investment Module

Input:
Risk category
Goal priorities
Monthly savings

Output:
Asset allocation:
Equity %
Debt %
Cash %
