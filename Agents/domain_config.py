"""Shared configuration for NEXUS domain agents and frontend navigation."""

DOMAIN_REGISTRY = {
    "Engineering": {
        "capabilities": [
            "Code Intelligence",
            "Architecture",
            "QA & Testing",
            "DevOps & Platform",
            "Security",
            "Data & AI",
        ],

        "quick_actions": [
            ("Analyze Architecture", "Architecture analysis of uploaded engineering knowledge."),
            ("Extract APIs", "Extract documented API endpoints, methods, parameters and purpose."),
            ("Find Technical Risks", "Identify technical risks, dependencies, gaps and potential failure points."),
            ("Explain Documentation", "Create a concise technical summary of relevant documentation."),
        ],    },
    "Product": {
        "capabilities": [
            "Product Strategy",
            "Requirements & PRD",
            "Roadmap",
            "UX & Research",
            "Product Analytics",
        ],

        "quick_actions": [
            ("Analyze Customer Feedback", "Cluster themes, pain points and evidence in customer feedback."),
            ("Extract Feature Requests", "Extract requested features with supporting evidence and frequency."),
            ("Generate Product Brief", "Generate a concise product brief grounded in uploaded evidence."),
            ("Generate PRD", "Draft a requirements document grounded in available product evidence."),
            ("Generate User Stories", "Turn documented requirements and feedback into user stories."),
        ],    },
    "People / HR": {
        "capabilities": [
            "HR Policies",
            "Recruitment",
            "Performance",
            "Compensation & Benefits",
            "Employee Relations",
        ],

        "quick_actions": [
            ("Analyze HR Policy", "Summarize policy rules, scope, exceptions and implications."),
            ("Compare Policies", "Compare relevant HR policies and identify differences and conflicts."),
            ("Generate Employee FAQ", "Generate employee-facing FAQs from documented HR policies."),
            ("Extract Requirements & Dates", "Extract requirements, eligibility rules and important dates."),
        ],    },
    "Finance": {
        "capabilities": [
            "Budgeting",
            "Expenses",
            "Revenue & Forecasting",
            "Procurement",
            "Financial Analysis",
        ],

        "quick_actions": [
            ("Extract Financial KPIs", "Extract documented financial KPIs, values, periods and units."),
            ("Analyze Financial Report", "Analyze the uploaded financial report and summarize key signals."),
            ("Compare Reports", "Compare relevant financial reports or periods and metrics."),
            ("Find Financial Signals", "Identify unusual movements, inconsistencies or signals requiring review."),
        ],    },
    "Legal & Compliance": {
        "capabilities": [
            "Contracts & NDAs",
            "Privacy & Data Protection",
            "Compliance",
            "Regulatory",
            "Risk & Audit",
        ],

        "quick_actions": [
            ("Review Contract", "Analyze key contract terms, parties, scope and documented risks."),
            ("Find Risky Clauses", "Identify clauses that may create contractual or compliance risk."),
            ("Compare Contracts", "Compare relevant contracts and highlight substantive differences."),
            ("Extract Obligations", "Extract obligations, responsible parties, conditions and consequences."),
            ("Extract Deadlines", "Extract important dates, notice periods, renewal dates and deadlines."),
        ],    },
}
