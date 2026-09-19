"""Reusable Phase 2 domain-intelligence actions built on the existing RAG pipeline."""

from Agents.domain_config import DOMAIN_REGISTRY
from Agents.engineering import engineering_agent
from Agents.product import product_agent
from Agents.people_hr import people_agent
from Agents.finance import finance_agent
from Agents.legal_compliance import legal_compliance_agent

ACTION_DEFINITIONS = {
    "Engineering": {
        "Analyze Architecture": "Analyze system architecture, components, interfaces, dependencies, data flows, bottlenecks and documented design decisions.",
        "Extract APIs": "Extract documented APIs/endpoints with method, path, purpose, parameters, authentication and response behavior. Do not invent missing fields.",
        "Find Technical Risks": "Identify technical risks, dependencies, single points of failure, security concerns, operational gaps and undocumented assumptions. Separate evidence from analysis.",
        "Explain Documentation": "Produce a concise technical summary covering purpose, components, workflows, configuration, dependencies and important implementation details.",
    },
    "Product": {
        "Analyze Customer Feedback": "Analyze customer feedback by themes, pain points, affected users, evidence and recurring signals. Do not treat frequency as importance unless documented.",
        "Extract Feature Requests": "Extract requested features with evidence, affected users, frequency when available, and stated problem.",
        "Generate Product Brief": "Generate a product brief with problem, target users, evidence, proposed outcome, scope, constraints and open questions.",
        "Generate PRD": "Generate a grounded PRD with problem, goals, non-goals, users, requirements, acceptance criteria, dependencies and open questions.",
        "Generate User Stories": "Generate user stories from documented requirements or feedback with acceptance criteria and supporting evidence.",
    },
    "People / HR": {
        "Analyze HR Policy": "Analyze policy scope, rules, eligibility, exceptions, responsibilities, procedures and employee impact using documented facts.",
        "Compare Policies": "Compare policies by scope, eligibility, rules, exceptions, responsibilities and effective dates. Identify differences and conflicts.",
        "Generate Employee FAQ": "Generate employee-facing questions and answers grounded in HR policy documents. Do not invent policy.",
        "Extract Requirements & Dates": "Extract eligibility requirements, responsibilities, required actions, effective dates and important deadlines.",
    },
    "Finance": {
        "Extract Financial KPIs": "Extract documented financial KPIs with metric name, value, period, unit/currency and source evidence. Preserve numbers exactly.",
        "Analyze Financial Report": "Analyze documented revenue, expenses, profitability, cash and other relevant metrics and explain notable movements without inventing causes.",
        "Compare Reports": "Compare relevant reports or periods across documented metrics. Show changes and cite evidence; distinguish arithmetic observations from interpretation.",
        "Find Financial Signals": "Identify unusual movements, inconsistencies, missing values or other signals worth review. Do not label something fraudulent or erroneous without evidence.",
    },
    "Legal & Compliance": {
        "Review Contract": "Review parties, scope, term, payment, termination, liability, confidentiality, governing law and other material documented terms.",
        "Find Risky Clauses": "Identify clauses that may create contractual or compliance risk, explain why they deserve review, and cite supporting evidence.",
        "Compare Contracts": "Compare relevant contracts focusing on material differences, conflicts and missing provisions.",
        "Extract Obligations": "Extract obligations with responsible party, action, trigger/condition, timing and consequence when documented.",
        "Extract Deadlines": "Extract effective dates, expiry/renewal dates, notice periods, payment dates, milestones and other deadlines. Do not infer dates.",
    },
}

def run_domain_action(domain: str, action: str) -> dict:
    if domain not in DOMAIN_REGISTRY:
        raise ValueError(f"Unknown NEXUS domain: {domain}")
    if action not in ACTION_DEFINITIONS.get(domain, {}):
        raise ValueError(f"Unsupported action for {domain}: {action}")
    instruction = ACTION_DEFINITIONS[domain][action]
    prompt = f"""You are the NEXUS {domain} Intelligence Agent.\n\nACTION: {action}\n\nTASK:\n{instruction}\n\nGROUNDING RULES:\n- Use ONLY retrieved documents for company-specific facts.\n- Clearly separate 'Documented facts' from 'AI analysis / interpretation'.\n- If evidence is insufficient, say so explicitly.\n- Never fabricate values, clauses, requirements, dates, endpoints or decisions.\n- Preserve source attribution.\n- Return a useful structured result for the user.\n"""
    # Reuse the existing domain agents so Phase 2 stays inside the
    # established orchestration + RAG architecture.
    if domain == "Engineering":
        result = engineering_agent(prompt)
    elif domain == "Product":
        result = product_agent(prompt)
    elif domain == "People / HR":
        result = people_agent(prompt)
    elif domain == "Finance":
        result = finance_agent(prompt)
    elif domain == "Legal & Compliance":
        result = legal_compliance_agent(prompt)
    else:
        raise ValueError(f"Unsupported NEXUS domain: {domain}")

    result["domain"] = domain
    result["action"] = action
    result["action_type"] = "domain_intelligence"
    return result
