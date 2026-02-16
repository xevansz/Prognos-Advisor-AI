import json

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def generate_prognosis_report(input_data: dict) -> dict:
    """
    Generate a prognosis report using LLM (Narrator agent).
    
    For MVP, this is a placeholder that returns structured output.
    Future: Integrate with Google Gemini Flash or other LLM providers.
    """
    
    system_prompt = """You are a financial planning assistant. Analyze the provided data and generate a clear, 
    non-judgmental financial prognosis report. Always emphasize that this is not financial advice.
    
    Return a JSON object with these fields:
    - summary_bullets: array of 3-8 key points
    - cashflow_section: string describing cash flow situation
    - goals_section: string describing goal feasibility
    - allocation_section: string describing recommended allocation
    - changes_since_last: string describing changes (or empty if first report)
    - disclaimer: string with appropriate disclaimer
    - markdown_body: optional full markdown report
    """
    
    try:
        if settings.llm_provider == "gemini" and settings.llm_api_key:
            import google.generativeai as genai
            
            genai.configure(api_key=settings.llm_api_key)
            model = genai.GenerativeModel(settings.llm_model)
            
            prompt = f"{system_prompt}\n\nInput data:\n{json.dumps(input_data, indent=2)}"
            response = model.generate_content(prompt)
            
            return json.loads(response.text)
        else:
            return _generate_mock_report(input_data)
            
    except Exception as e:
        logger.error(f"Failed to generate LLM report: {e}")
        return _generate_mock_report(input_data)


def _generate_mock_report(input_data: dict) -> dict:
    """
    Generate a mock report for testing without LLM API.
    """
    return {
        "summary_bullets": [
            "Your financial situation has been analyzed",
            "Risk capacity and burn rate have been calculated",
            "Goal feasibility has been assessed",
            "Asset allocation recommendations are provided below",
        ],
        "cashflow_section": "Based on recent transactions, your monthly cash flow appears stable.",
        "goals_section": "Your goals have been evaluated based on current savings rate.",
        "allocation_section": "A diversified allocation strategy is recommended based on your risk profile.",
        "changes_since_last": "This is your first prognosis report.",
        "disclaimer": "This analysis is for informational purposes only and does not constitute financial advice. "
                     "Consult with a qualified financial advisor before making investment decisions.",
        "markdown_body": None,
    }
