"""
NEXUS - Legal & Compliance Agent
"""

from rag import answer_question


LEGAL_AREAS = [
    "Policies",
    "Compliance",
    "Contracts",
    "Privacy",
    "Risk",
    "Regulatory Requirements",
]


def detect_legal_area(question: str):
    """
    Detect the relevant Legal / Compliance area.
    """

    q = question.lower()

    keywords = {
        "Policies": [
            "policy",
            "policies",
            "terms",
            "guideline",
        ],
        "Compliance": [
            "compliance",
            "compliant",
            "audit",
            "control",
        ],
        "Contracts": [
            "contract",
            "agreement",
            "nda",
            "clause",
            "vendor agreement",
        ],
        "Privacy": [
            "privacy",
            "personal data",
            "pii",
            "data protection",
            "gdpr",
            "consent",
        ],
        "Risk": [
            "risk",
            "legal risk",
            "exposure",
            "liability",
        ],
        "Regulatory Requirements": [
            "regulation",
            "regulatory",
            "law",
            "legal requirement",
            "statutory",
        ],
    }

    for area, terms in keywords.items():
        if any(term in q for term in terms):
            return area

    return None


def legal_compliance_agent(question: str, area=None) -> dict:
    """
    Process a Legal & Compliance question.
    """

    if not question or not question.strip():
        return {
            "answer": "Please provide a Legal & Compliance question.",
            "domain": "Legal & Compliance",
            "capability": area,
            "agent": "legal_compliance",
            "path": "legal_compliance",
        }

    question = question.strip()

    detected_area = area or detect_legal_area(question)

    context = ""

    if detected_area:
        context = (
            f"\n\nLegal / Compliance focus area: {detected_area}.\n"
            "Use the company's authorized documents as the primary "
            "source. Do not invent legal requirements or contractual "
            "terms. Clearly identify uncertainty where the documents "
            "do not provide an answer.\n"
        )

    enhanced_question = (
        "You are the NEXUS Legal & Compliance Agent.\n"
        "Answer based on authorized company knowledge and retrieved "
        "documents. This is an internal knowledge assistant and not "
        "a substitute for professional legal advice.\n"
        f"{context}\n"
        f"User question:\n{question}"
    )

    result = answer_question(enhanced_question)

    result["domain"] = "Legal & Compliance"
    result["capability"] = detected_area
    result["agent"] = "legal_compliance"

    return result