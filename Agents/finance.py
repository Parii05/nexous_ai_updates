"""
NEXUS - Finance Agent
"""

from rag import answer_question


FINANCE_AREAS = [
    "Budgets",
    "Expenses",
    "Financial Planning",
    "Procurement",
    "Reporting",
    "Forecasting",
]


def detect_finance_area(question: str):
    """
    Detect the relevant Finance area.
    """

    q = question.lower()

    keywords = {
        "Budgets": [
            "budget",
            "budgets",
            "allocated",
            "allocation",
        ],
        "Expenses": [
            "expense",
            "expenses",
            "spending",
            "cost",
            "reimbursement",
        ],
        "Financial Planning": [
            "financial plan",
            "planning",
            "financial strategy",
        ],
        "Procurement": [
            "procurement",
            "purchase",
            "purchasing",
            "vendor",
            "supplier",
        ],
        "Reporting": [
            "financial report",
            "reporting",
            "revenue",
            "profit",
            "loss",
            "statement",
        ],
        "Forecasting": [
            "forecast",
            "forecasting",
            "projection",
            "projected",
        ],
    }

    for area, terms in keywords.items():
        if any(term in q for term in terms):
            return area

    return None


def finance_agent(question: str, area=None) -> dict:
    """
    Process a Finance question.
    """

    if not question or not question.strip():
        return {
            "answer": "Please provide a finance-related question.",
            "domain": "Finance",
            "capability": area,
            "agent": "finance",
            "path": "finance",
        }

    question = question.strip()

    detected_area = area or detect_finance_area(question)

    context = ""

    if detected_area:
        context = (
            f"\n\nFinance focus area: {detected_area}.\n"
            "Use documented financial information when available. "
            "Do not fabricate financial figures, budgets or forecasts.\n"
        )

    enhanced_question = (
        "You are the NEXUS Finance Agent.\n"
        "Answer using authorized company knowledge and retrieved "
        "documents. Preserve financial figures and terminology exactly "
        "when supported by the documents.\n"
        f"{context}\n"
        f"User question:\n{question}"
    )

    result = answer_question(
        enhanced_question,
        domain="Finance",
    )

    result["domain"] = "Finance"
    result["capability"] = detected_area
    result["agent"] = "finance"

    return result