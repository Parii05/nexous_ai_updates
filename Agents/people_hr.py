"""
NEXUS - People / HR Agent
"""

from rag import answer_question


PEOPLE_AREAS = [
    "Employee Policies",
    "Benefits",
    "Leave & Attendance",
    "Performance",
    "Recruitment",
    "Learning & Development",
]


def detect_people_area(question: str):
    """
    Detect the relevant People / HR area.
    """

    q = question.lower()

    keywords = {
        "Employee Policies": [
            "policy",
            "employee policy",
            "workplace",
            "employee handbook",
            "hr policy",
        ],
        "Benefits": [
            "benefit",
            "insurance",
            "health benefit",
            "allowance",
            "perks",
        ],
        "Leave & Attendance": [
            "leave",
            "vacation",
            "holiday",
            "attendance",
            "parental leave",
            "sick leave",
            "maternity",
            "paternity",
        ],
        "Performance": [
            "performance",
            "appraisal",
            "review",
            "promotion",
            "performance review",
        ],
        "Recruitment": [
            "recruitment",
            "hiring",
            "interview",
            "candidate",
            "job",
            "recruit",
        ],
        "Learning & Development": [
            "training",
            "learning",
            "development",
            "course",
            "skill",
        ],
    }

    for area, terms in keywords.items():
        if any(term in q for term in terms):
            return area

    return None


def people_agent(question: str, area=None) -> dict:
    """
    Process a People / HR question.
    """

    if not question or not question.strip():
        return {
            "answer": "Please provide a People / HR question.",
            "domain": "People / HR",
            "capability": area,
            "agent": "people",
            "path": "people",
        }

    question = question.strip()

    detected_area = area or detect_people_area(question)

    context = ""

    if detected_area:
        context = (
            f"\n\nPeople / HR focus area: {detected_area}.\n"
            "Prioritize official company policies and documented HR "
            "information. Do not invent employee benefits or policies.\n"
        )

    enhanced_question = (
        "You are the NEXUS People / HR Agent.\n"
        "Answer using authorized company knowledge and retrieved "
        "documents. If a policy is not present in the available "
        "documents, explicitly say so.\n"
        f"{context}\n"
        f"User question:\n{question}"
    )

    result = answer_question(
        enhanced_question,
        domain="People / HR",
    )

    result["domain"] = "People / HR"
    result["capability"] = detected_area
    result["agent"] = "people"

    return result