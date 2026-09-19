"""AI-generated, document-grounded dashboard intelligence for NEXUS Phase 3."""

import json
import re

from Agents.domain_config import DOMAIN_REGISTRY
from Agents.engineering import engineering_agent
from Agents.product import product_agent
from Agents.people_hr import people_agent
from Agents.finance import finance_agent
from Agents.legal_compliance import legal_compliance_agent


DASHBOARD_DEFINITIONS = {
    "Engineering": {
        "title": "Engineering AI Insights",
        "sections": {
            "Technologies & Components": "List technologies, frameworks, libraries, infrastructure components and major system components explicitly present in the documents.",
            "Architecture Insights": "Summarize documented architecture, component relationships, data flows and design decisions. Separate observations from interpretation.",
            "Engineering Risks": "Identify documented or evidence-based technical risks, dependencies, gaps and failure points. Do not invent vulnerabilities.",
            "APIs & Services": "Extract documented APIs, endpoints, services, methods and purposes. Do not invent missing fields.",
            "Recommendations": "Give practical recommendations derived from the documented evidence. Mark these as AI-generated recommendations, not document facts.",
        },
    },
    "Product": {
        "title": "Product AI Insights",
        "sections": {
            "Key Product Themes": "Identify recurring product themes and topics supported by the documents.",
            "Feature Requests": "Extract documented feature requests and supporting evidence.",
            "Customer / User Problems": "Identify documented customer or user pain points and problems.",
            "Opportunities": "Identify opportunities that follow from documented evidence. Clearly label these as AI interpretation.",
            "Product Recommendations": "Give practical AI-generated recommendations grounded in the documents.",
        },
    },
    "People / HR": {
        "title": "People & HR AI Insights",
        "sections": {
            "Policies Identified": "List HR policies and policy areas explicitly present in the documents.",
            "Benefits": "Extract documented benefits, allowances and employee provisions.",
            "Employee Requirements": "Extract eligibility rules, employee responsibilities and required actions.",
            "Important Dates": "Extract effective dates, deadlines, review dates and other dates explicitly present.",
            "Policy Insights": "Summarize implications and notable policy observations, clearly separating AI interpretation from documented facts.",
        },
    },
    "Finance": {
        "title": "Finance AI Insights",
        "sections": {
            "Financial KPIs": "Extract revenue, expenses, profit, margins, cash and other financial KPIs with exact values, periods and units when available.",
            "Financial Trends": "Describe documented changes over time. Do not invent causes.",
            "Anomalies / Signals": "Identify unusual movements, inconsistencies or signals supported by the documents. Do not call something fraud or an error without evidence.",
            "Key Financial Insights": "Summarize the most important documented financial observations and clearly mark interpretation.",
        },
    },
    "Legal & Compliance": {
        "title": "Legal & Compliance AI Insights",
        "sections": {
            "Contract / Policy Information": "Extract document type, parties, scope, term, effective date and other material information when present.",
            "Important Clauses": "Extract material clauses such as termination, liability, confidentiality, payment, governing law and compliance provisions.",
            "Obligations": "Extract obligations with responsible party, trigger, timing and consequence when documented.",
            "Deadlines": "Extract notice periods, expiry, renewal, payment dates, milestones and other explicit deadlines.",
            "Potential Risk Areas": "Identify clauses or provisions that deserve review based on documented evidence. Do not make definitive legal conclusions.",
        },
    },
}


def _extract_json(text: str) -> dict | None:
    """Parse JSON even when the model wraps it in a markdown fence."""
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^\\s*json\\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\\s*$", "", cleaned)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\\{.*\\}", cleaned, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def run_domain_dashboard(domain: str) -> dict:
    if domain not in DOMAIN_REGISTRY:
        raise ValueError(f"Unknown NEXUS domain: {domain}")

    definition = DASHBOARD_DEFINITIONS[domain]
    section_schema = {
        name: {"items": ["short, factual item", "another item"], "status": "available or unavailable"}
        for name in definition["sections"]
    }

    prompt = (
        "You are the NEXUS " + domain + " Dashboard Intelligence Agent.\n\n"
        "Build a dashboard from ONLY the retrieved company documents for the " + domain + " domain.\n\n"
        "Return VALID JSON ONLY with this exact top-level shape:\n"
        + json.dumps({
            "document_status": "available or unavailable",
            "sections": section_schema,
            "documented_facts": ["fact 1"],
            "ai_insights": ["insight 1"],
            "recommendations": ["recommendation 1"],
        }, indent=2)
        + "\n\nRules:\n"
        "- Every company-specific fact must be supported by retrieved documents.\n"
        "- If the documents do not contain evidence for a section, return an empty items list and status \"unavailable\".\n"
        "- Never invent values, technologies, APIs, customers, policies, financial numbers, clauses, dates or requirements.\n"
        "- Preserve exact financial numbers, units and periods when present.\n"
        "- Keep documented facts separate from AI-generated insights and recommendations.\n"
        "- Recommendations are AI-generated and must be grounded in the available evidence.\n"
        "- If there are no documents/evidence, say so through document_status and unavailable sections.\n"
        "- Do not output markdown, explanations or reasoning outside the JSON.\n\n"
        "Domain sections:\n"
        + "\n".join("- " + name + ": " + desc for name, desc in definition["sections"].items())
    )

    agents = {
        "Engineering": engineering_agent,
        "Product": product_agent,
        "People / HR": people_agent,
        "Finance": finance_agent,
        "Legal & Compliance": legal_compliance_agent,
    }

    result = agents[domain](prompt)
    answer = result.get("answer", "")
    parsed = _extract_json(answer)

    if parsed is None:
        parsed = {
            "document_status": "available" if result.get("citations") else "unavailable",
            "sections": {
                name: {"items": [], "status": "unavailable"}
                for name in definition["sections"]
            },
            "documented_facts": [],
            "ai_insights": [answer] if answer else [],
            "recommendations": [],
        }

    parsed["domain"] = domain
    parsed["title"] = definition["title"]
    parsed["citations"] = result.get("citations", [])
    parsed["sources"] = result.get("sources", [])
    parsed["confidence"] = result.get("confidence", 0.0)
    parsed["grounded"] = bool(result.get("citations"))
    return parsed
