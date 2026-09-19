"""
NEXUS - Product Agent
"""

from rag import answer_question


PRODUCT_AREAS = [
    "Product Strategy",
    "Roadmaps",
    "Requirements",
    "Features",
    "User Experience",
    "Product Analytics",
]


def detect_product_area(question: str):
    """
    Detect the most relevant Product area.
    """

    q = question.lower()

    keywords = {
        "Product Strategy": [
            "strategy",
            "product strategy",
            "market",
            "vision",
            "product goal",
        ],
        "Roadmaps": [
            "roadmap",
            "milestone",
            "release",
            "timeline",
            "launch",
        ],
        "Requirements": [
            "requirement",
            "requirements",
            "prd",
            "specification",
            "acceptance criteria",
        ],
        "Features": [
            "feature",
            "functionality",
            "feature request",
            "enhancement",
        ],
        "User Experience": [
            "ux",
            "ui",
            "user experience",
            "user journey",
            "usability",
        ],
        "Product Analytics": [
            "analytics",
            "metric",
            "metrics",
            "conversion",
            "retention",
            "kpi",
        ],
    }

    for area, terms in keywords.items():
        if any(term in q for term in terms):
            return area

    return None


def product_agent(question: str, area=None) -> dict:
    """
    Process a Product question.
    """

    if not question or not question.strip():
        return {
            "answer": "Please provide a product-related question.",
            "domain": "Product",
            "capability": area,
            "agent": "product",
            "path": "product",
        }

    question = question.strip()

    detected_area = area or detect_product_area(question)

    context = ""

    if detected_area:
        context = (
            f"\n\nProduct focus area: {detected_area}.\n"
            "Prioritize relevant product requirements, roadmap information, "
            "business context and documented decisions.\n"
        )

    enhanced_question = (
        "You are the NEXUS Product Agent.\n"
        "Answer the user's question using available company knowledge "
        "and retrieved documents. Clearly distinguish documented facts "
        "from uncertainty.\n"
        f"{context}\n"
        f"User question:\n{question}"
    )

    result = answer_question(enhanced_question)

    result["domain"] = "Product"
    result["capability"] = detected_area
    result["agent"] = "product"

    return result