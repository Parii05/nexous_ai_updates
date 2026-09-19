"""
NEXUS - Orchestrator Agent

The orchestrator is the entry point for user questions.

Responsibilities:
1. Understand the user's question.
2. Select the appropriate domain agent.
3. Send the question to that domain agent.
4. Return a unified response to the API/frontend.
"""

from typing import Optional


from Agents.engineering import engineering_agent
from Agents.product import product_agent
from Agents.people_hr import people_agent
from Agents.finance import finance_agent
from Agents.legal_compliance import legal_compliance_agent


DOMAINS = [
    "Engineering",
    "Product",
    "People / HR",
    "Finance",
    "Legal & Compliance",
]


def detect_domain(question: str) -> str:
    """
    Determine which domain should handle the question.

    This is intentionally simple for the first version.
    Later, this can be replaced with an LLM-based router.
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # ENGINEERING
    # ---------------------------------------------------------

    engineering_keywords = [
        "code",
        "coding",
        "programming",
        "python",
        "java",
        "javascript",
        "software",
        "bug",
        "debug",
        "api",
        "architecture",
        "system design",
        "database",
        "testing",
        "qa",
        "devops",
        "deployment",
        "docker",
        "kubernetes",
        "cloud",
        "machine learning",
        "ml",
        "llm",
        "ai",
        "model",
        "embedding",
        "data pipeline",
    ]

    # ---------------------------------------------------------
    # PRODUCT
    # ---------------------------------------------------------

    product_keywords = [
        "product",
        "roadmap",
        "feature",
        "features",
        "requirement",
        "requirements",
        "prd",
        "user story",
        "release",
        "launch",
        "ux",
        "user experience",
        "product strategy",
        "product metric",
    ]

    # ---------------------------------------------------------
    # PEOPLE / HR
    # ---------------------------------------------------------

    people_keywords = [
        "employee",
        "employees",
        "hr",
        "human resources",
        "leave",
        "parental leave",
        "maternity",
        "paternity",
        "attendance",
        "salary",
        "benefit",
        "benefits",
        "appraisal",
        "performance review",
        "recruitment",
        "hiring",
        "employee policy",
        "workplace policy",
    ]

    # ---------------------------------------------------------
    # FINANCE
    # ---------------------------------------------------------

    finance_keywords = [
        "finance",
        "financial",
        "budget",
        "budgets",
        "expense",
        "expenses",
        "cost",
        "revenue",
        "profit",
        "loss",
        "forecast",
        "forecasting",
        "procurement",
        "purchase",
        "purchasing",
        "financial report",
        "allocation",
    ]

    # ---------------------------------------------------------
    # LEGAL / COMPLIANCE
    # ---------------------------------------------------------

    legal_keywords = [
        "legal",
        "law",
        "compliance",
        "contract",
        "contracts",
        "agreement",
        "nda",
        "privacy",
        "gdpr",
        "data protection",
        "regulation",
        "regulatory",
        "liability",
        "legal risk",
        "audit",
    ]

    # ---------------------------------------------------------
    # SCORE EACH DOMAIN
    # ---------------------------------------------------------

    scores = {
        "Engineering": 0,
        "Product": 0,
        "People / HR": 0,
        "Finance": 0,
        "Legal & Compliance": 0,
    }

    for keyword in engineering_keywords:
        if keyword in q:
            scores["Engineering"] += 1

    for keyword in product_keywords:
        if keyword in q:
            scores["Product"] += 1

    for keyword in people_keywords:
        if keyword in q:
            scores["People / HR"] += 1

    for keyword in finance_keywords:
        if keyword in q:
            scores["Finance"] += 1

    for keyword in legal_keywords:
        if keyword in q:
            scores["Legal & Compliance"] += 1

    # ---------------------------------------------------------
    # SELECT BEST DOMAIN
    # ---------------------------------------------------------

    best_domain = max(scores, key=scores.get)

    # No domain-specific keywords.
    # Default to Engineering because NEXUS is currently
    # being developed around the engineering/RAG workflow.
    if scores[best_domain] == 0:
        return "Engineering"

    return best_domain


def route_question(
    question: str,
    selected_domain: Optional[str] = None,
    capability: Optional[str] = None,
) -> dict:
    """
    Route a question to the appropriate domain agent.

    Args:
        question:
            User's question.

        selected_domain:
            Optional domain explicitly selected in the UI.

        capability:
            Optional capability selected in the UI.

    Returns:
        Structured response dictionary.
    """

    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "domain": None,
            "agent": "orchestrator",
            "path": "orchestrator",
            "confidence": 0.0,
            "citations": [],
        }

    question = question.strip()

    # ---------------------------------------------------------
    # DOMAIN SELECTION
    # ---------------------------------------------------------

    if selected_domain and selected_domain in DOMAINS:
        domain = selected_domain
    else:
        domain = detect_domain(question)

    # ---------------------------------------------------------
    # ROUTE TO AGENT
    # ---------------------------------------------------------

    if domain == "Engineering":

        result = engineering_agent(
            question,
            capability=capability,
        )

    elif domain == "Product":

        result = product_agent(
            question,
            area=capability,
        )

    elif domain == "People / HR":

        result = people_agent(
            question,
            area=capability,
        )

    elif domain == "Finance":

        result = finance_agent(
            question,
            area=capability,
        )

    elif domain == "Legal & Compliance":

        result = legal_compliance_agent(
            question,
            area=capability,
        )

    else:

        return {
            "answer": "I could not determine the appropriate NEXUS domain.",
            "domain": None,
            "agent": "orchestrator",
            "path": "orchestrator",
            "confidence": 0.0,
            "citations": [],
        }

    # ---------------------------------------------------------
    # ADD ORCHESTRATOR METADATA
    # ---------------------------------------------------------

    result["orchestrator"] = "orchestrator"
    result["selected_domain"] = domain

    return result


def orchestrator_agent(
    question: str,
    selected_domain: Optional[str] = None,
    capability: Optional[str] = None,
) -> dict:
    """
    Public entry point for the NEXUS orchestrator.
    """

    return route_question(
        question=question,
        selected_domain=selected_domain,
        capability=capability,
    )