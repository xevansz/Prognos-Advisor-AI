import json

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def generate_prognosis_report(input_data: dict) -> dict:
    """
    Generate a prognosis report using LLM (Narrator agent).

    Uses actual user financial data to provide personalized insights and recommendations.
    """

    try:
        if settings.llm_provider == "gemini" and settings.llm_api_key:
            from google import genai

            client = genai.Client(api_key=settings.llm_api_key)

            system_instruction = """You are an expert financial advisor AI analyzing a user's financial situation. 
Your role is to provide clear, actionable insights based on their accounts, transactions, goals, and risk profile.

IMPORTANT: You must return ONLY a valid JSON object with NO additional text, markdown formatting, or code blocks.

Analyze the provided financial data and generate a comprehensive report with these exact fields:
{
  "summary_bullets": ["array of 4-7 key insights about their financial situation"],
  "cashflow_section": "2-3 paragraph analysis of income, expenses, savings rate, 
    and cash flow patterns",
  "goals_section": "2-3 paragraph analysis of goal feasibility, required savings, 
    and recommendations",
  "allocation_section": "2-3 paragraph explanation of recommended asset allocation 
    and investment strategy",
  "changes_since_last": "1-2 paragraphs comparing to previous report 
    (or 'This is your first prognosis report.' if no previous data)",
  "disclaimer": "Standard disclaimer that this is informational only, not financial advice",
  "markdown_body": "Full detailed markdown report with sections: ## Financial Overview, ## Cash Flow Analysis,
  ## Goal Progress, ## Investment Strategy, ## Action Items"
}

Guidelines:
- Be specific with numbers and percentages from the actual data
- Provide actionable recommendations based on their risk profile and goals
- Highlight both strengths and areas for improvement
- Use encouraging but realistic language
- If data is limited (no transactions/accounts), acknowledge this and provide general guidance
- Focus on wealth-building strategies aligned with their risk appetite and goals"""

            user_prompt = f"""{system_instruction}

Analyze this financial data and generate a personalized report:

USER PROFILE:
- Age: {input_data.get("profile", {}).get("age", "N/A")}
- Base Currency: {input_data.get("profile", {}).get("base_currency", "USD")}
- Risk Appetite: {input_data.get("profile", {}).get("risk_appetite", "moderate")}

RISK METRICS:
{json.dumps(input_data.get("risk", {}), indent=2)}

GOALS EVALUATION:
{json.dumps(input_data.get("goals", []), indent=2)}

RECOMMENDED ALLOCATION:
{json.dumps(input_data.get("allocation", {}), indent=2)}

RL STRATEGY RECOMMENDATION:
{json.dumps(input_data.get("strategy", {}), indent=2)}

ACCOUNTS & TRANSACTIONS:
{json.dumps(input_data.get("accounts_summary", {}), indent=2)}

PREVIOUS REPORT (for comparison):
{json.dumps(input_data.get("previous_report", "None - First report"), indent=2)}

Generate the JSON report now:"""

            response = client.models.generate_content(
                model=settings.llm_model,
                contents=user_prompt,
                config={
                    "temperature": 0.7,
                    "response_mime_type": "application/json",
                },
            )

            report_text = response.text.strip()
            if report_text.startswith("```"):
                report_text = report_text.split("```")[1]
                if report_text.startswith("json"):
                    report_text = report_text[4:]
                report_text = report_text.strip()

            return json.loads(report_text)
        else:
            logger.warning("LLM not configured, using enhanced fallback report generator")
            return _generate_enhanced_report(input_data)

    except Exception as e:
        logger.error(f"Failed to generate LLM report: {e}")
        return _generate_enhanced_report(input_data)


def _generate_enhanced_report(input_data: dict) -> dict:
    """
    Generate an enhanced fallback report using actual user data when LLM is unavailable.
    """
    profile = input_data.get("profile", {})
    risk = input_data.get("risk", {})
    goals = input_data.get("goals", [])
    allocation = input_data.get("allocation", {})
    strategy = input_data.get("strategy", {})
    accounts_summary = input_data.get("accounts_summary", {})

    # Extract key metrics
    risk_score = risk.get("risk_score", 50)
    risk_label = risk.get("risk_label", "Moderate")
    runway_months = risk.get("runway_months", 0)
    savings_ratio = risk.get("savings_ratio", 0)
    stability_ratio = risk.get("stability_ratio", 1.0)

    age = profile.get("age", 35)
    risk_appetite = profile.get("risk_appetite", "moderate")
    currency = profile.get("base_currency", "USD")

    recommended = allocation.get("recommended", {})
    equity_pct = int(recommended.get("equity", 0.5) * 100)
    debt_pct = int(recommended.get("debt", 0.3) * 100)
    cash_pct = int(recommended.get("cash", 0.15) * 100)

    strategy_action = strategy.get("action", "keep_strategy")

    num_accounts = accounts_summary.get("num_accounts", 0)
    num_transactions = accounts_summary.get("num_transactions", 0)
    monthly_income = accounts_summary.get("monthly_income", 0)
    monthly_expenses = accounts_summary.get("monthly_expenses", 0)

    # Build summary bullets
    summary_bullets = []

    if num_accounts == 0 and num_transactions == 0:
        summary_bullets.append(
            "No accounts or transactions found - add your financial data to get personalized insights"
        )
        summary_bullets.append(f"Your risk profile is set to '{risk_appetite}' with a risk score of {risk_score}/100")
    else:
        summary_bullets.append(
            f"Risk Assessment: {risk_label} risk ({risk_score}/100) based on your financial situation"
        )
        if savings_ratio > 0:
            summary_bullets.append(
                f"You're saving {int(savings_ratio * 100)}% of your income - "
                f"{'excellent' if savings_ratio > 0.2 else 'good' if savings_ratio > 0.1 else 'consider increasing'}"
            )
        if runway_months > 0 and runway_months < 999:
            summary_bullets.append(
                f"Emergency fund covers {runway_months:.1f} months of expenses - "
                f"{'strong position' if runway_months >= 6 else 'build up to 6+ months'}"
            )

    if goals:
        on_track = sum(1 for g in goals if g.get("status") == "on_track")
        at_risk = sum(1 for g in goals if g.get("status") == "at_risk")
        unrealistic = sum(1 for g in goals if g.get("status") == "unrealistic")

        if on_track > 0:
            summary_bullets.append(f"{on_track} of {len(goals)} goals are on track")
        if at_risk > 0:
            summary_bullets.append(f"{at_risk} goals need attention to stay on track")
        if unrealistic > 0:
            summary_bullets.append(f"{unrealistic} goals may need timeline or amount adjustments")
    else:
        summary_bullets.append("Add financial goals to get personalized savings recommendations")

    summary_bullets.append(f"Recommended allocation: {equity_pct}% equity, {debt_pct}% bonds, {cash_pct}% cash")

    if strategy_action == "increase_savings":
        summary_bullets.append("Strategy: Increase monthly savings by 5% to improve goal outcomes")
    elif strategy_action == "shift_to_equity":
        summary_bullets.append("Strategy: Shift 10% more to equity for better long-term growth")
    elif strategy_action == "shift_to_bonds":
        summary_bullets.append("Strategy: Shift 10% to bonds for more stability")

    # Build cashflow section
    if num_transactions == 0:
        cashflow_section = (
            "No transaction data available yet. Add your income and expense transactions to track "
            "cash flow patterns and get personalized insights.\n\n"
            "Once you add transactions, we'll analyze your spending patterns, identify savings "
            "opportunities, and help you optimize your monthly cash flow."
        )
    else:
        cashflow_section = (
            f"Based on {num_transactions} recent transactions, your monthly income is approximately "
            f"{currency} {monthly_income:,.0f} with expenses of {currency} {monthly_expenses:,.0f}. "
        )

        if savings_ratio > 0.2:
            cashflow_section += (
                f"You're saving {int(savings_ratio * 100)}% of your income, which is excellent. "
                f"This strong savings rate gives you flexibility to pursue your financial goals.\n\n"
            )
        elif savings_ratio > 0.1:
            cashflow_section += (
                f"You're saving {int(savings_ratio * 100)}% of your income. "
                f"Consider increasing this to 20% or more to accelerate wealth building.\n\n"
            )
        else:
            cashflow_section += (
                f"Your current savings rate is {int(savings_ratio * 100)}%. "
                f"Focus on reducing discretionary expenses to increase savings.\n\n"
            )

        if stability_ratio >= 1.5:
            cashflow_section += (
                f"Your income-to-expense ratio of {stability_ratio:.1f}x indicates strong financial "
                f"stability. You have good capacity to handle unexpected expenses."
            )
        elif stability_ratio >= 1.0:
            cashflow_section += (
                f"Your income covers expenses with a {stability_ratio:.1f}x ratio. "
                f"Building a larger buffer would improve financial resilience."
            )
        else:
            cashflow_section += (
                f"Your expenses exceed income (ratio: {stability_ratio:.1f}x). "
                f"Immediate action needed to reduce spending or increase income."
            )

    # Build goals section
    if not goals:
        goals_section = (
            "You haven't set any financial goals yet. Setting specific goals with target amounts and "
            "dates helps create a clear roadmap for your financial future.\n\n"
            "Consider adding goals like: emergency fund, down payment, retirement, education, "
            "or major purchases. We'll analyze feasibility and provide actionable savings plans."
        )
    else:
        goals_section = f"You have {len(goals)} active financial goals. "

        for goal in goals:
            goal_name = goal.get("goal_name", "Goal")
            status = goal.get("status", "unknown")
            success_prob = goal.get("success_probability", 0)
            required_savings = goal.get("required_monthly_savings", 0)
            actual_savings = goal.get("actual_monthly_savings", 0)

            if status == "on_track":
                goals_section += (
                    f"\n\n**{goal_name}**: On track with {int(success_prob * 100)}% success probability. "
                    f"Continue your current savings of {currency} {actual_savings:,.0f}/month."
                )
            elif status == "at_risk":
                goals_section += (
                    f"\n\n**{goal_name}**: At risk ({int(success_prob * 100)}% success probability). "
                    f"Increase savings from {currency} {actual_savings:,.0f} to "
                    f"{currency} {required_savings:,.0f}/month to get back on track."
                )
            else:
                goals_section += (
                    f"\n\n**{goal_name}**: Needs adjustment ({int(success_prob * 100)}% success probability). "
                    f"Required savings of {currency} {required_savings:,.0f}/month may be unrealistic. "
                    f"Consider extending timeline or reducing target amount."
                )

    # Build allocation section
    allocation_section = (
        f"Based on your age ({age}), {risk_appetite} risk appetite, and {risk_label.lower()} risk "
        f"capacity, we recommend a balanced portfolio allocation:\n\n"
        f"- **Equity ({equity_pct}%)**: Stocks and equity funds for long-term growth\n"
        f"- **Debt ({debt_pct}%)**: Bonds and fixed income for stability\n"
        f"- **Cash ({cash_pct}%)**: Liquid reserves for emergencies and opportunities\n\n"
    )

    if equity_pct >= 60:
        allocation_section += (
            "This growth-oriented allocation suits your profile and time horizon. "
            "Equity exposure provides inflation protection and wealth building potential."
        )
    elif equity_pct >= 40:
        allocation_section += (
            "This balanced allocation provides growth potential while managing volatility. "
            "Suitable for medium-term goals with moderate risk tolerance."
        )
    else:
        allocation_section += (
            "This conservative allocation prioritizes capital preservation. "
            "Appropriate given your risk profile, though it may limit long-term growth."
        )

    # Changes section
    has_previous = input_data.get("previous_report") is not None
    if has_previous:
        changes_since_last = (
            "This report reflects your updated financial situation. "
            "Compare key metrics with your previous report to track progress over time."
        )
    else:
        changes_since_last = "This is your first prognosis report."

    # Build markdown body
    markdown_body = f"""## Financial Overview

**Risk Profile**: {risk_label} ({risk_score}/100)  
**Risk Appetite**: {risk_appetite.title()}  
**Age**: {age}  
**Currency**: {currency}

{
        f"**Accounts**: {num_accounts} | **Transactions**: {num_transactions}"
        if num_accounts > 0
        else "**Status**: No accounts or transactions added yet"
    }

## Cash Flow Analysis

{cashflow_section}

## Goal Progress

{goals_section}

## Investment Strategy

{allocation_section}

## Action Items

Based on our analysis, here are recommended next steps:

"""

    if num_accounts == 0:
        markdown_body += "1. **Add your accounts** - Link bank accounts, investments, and other assets\n"
        markdown_body += "2. **Import transactions** - Add recent income and expenses for cash flow analysis\n"

    if not goals:
        markdown_body += "3. **Set financial goals** - Define targets with amounts and timelines\n"

    if strategy_action == "increase_savings":
        markdown_body += "4. **Increase savings rate** - Target 5% more of monthly income\n"
    elif strategy_action == "shift_to_equity":
        markdown_body += "4. **Rebalance portfolio** - Shift 10% more to equity for growth\n"
    elif strategy_action == "shift_to_bonds":
        markdown_body += "4. **Reduce risk exposure** - Move 10% to bonds for stability\n"

    if runway_months < 6 and runway_months > 0:
        markdown_body += "5. **Build emergency fund** - Target 6 months of expenses in liquid accounts\n"

    markdown_body += "\n*Review and adjust your plan quarterly as your situation evolves.*"

    return {
        "summary_bullets": summary_bullets,
        "cashflow_section": cashflow_section,
        "goals_section": goals_section,
        "allocation_section": allocation_section,
        "changes_since_last": changes_since_last,
        "disclaimer": (
            "This analysis is for informational purposes only and does not constitute financial advice. "
            "Consult with a qualified financial advisor before making investment decisions."
        ),
        "markdown_body": markdown_body,
    }


if __name__ == "__main__":
    print(repr(settings.llm_api_key))
