"""
NEXUS - Engineering Agent

Top-level domain:
    Engineering

Capabilities:
    - Code Intelligence
    - Architecture
    - QA & Testing
    - DevOps & Platform
    - Security
    - Data & AI
"""

from rag import answer_question


ENGINEERING_CAPABILITIES = [
    "Code Intelligence",
    "Architecture",
    "QA & Testing",
    "DevOps & Platform",
    "Security",
    "Data & AI",
]


# =========================================================
# CAPABILITY DETECTION
# =========================================================

def detect_engineering_capability(question: str) -> str | None:
    """
    Detect the most relevant Engineering capability.
    """

    q = question.lower()

    capability_keywords = {

        "Code Intelligence": [
            "code",
            "repository",
            "repo",
            "github",
            "function",
            "class",
            "module",
            "file",
            "commit",
            "pull request",
            "pr",
            "dependency",
            "dependencies",
            "implementation",
            "api endpoint",
            "source code",
        ],

        "Architecture": [
            "architecture",
            "system design",
            "design",
            "component",
            "service architecture",
            "microservice",
            "microservices",
            "data flow",
            "system flow",
            "sequence",
            "infrastructure architecture",
        ],

        "QA & Testing": [
            "test",
            "testing",
            "qa",
            "quality",
            "bug",
            "defect",
            "coverage",
            "unit test",
            "integration test",
            "regression",
            "test case",
            "test suite",
        ],

        "DevOps & Platform": [
            "deploy",
            "deployment",
            "devops",
            "ci/cd",
            "cicd",
            "pipeline",
            "docker",
            "kubernetes",
            "k8s",
            "cloud",
            "infrastructure",
            "server",
            "production",
            "release",
            "build",
        ],

        "Security": [
            "security",
            "authentication",
            "authorization",
            "access control",
            "rbac",
            "permission",
            "permissions",
            "credential",
            "credentials",
            "password",
            "login",
            "identity",
            "iam",
            "oauth",
            "oauth2",
            "jwt",
            "token",
            "encryption",
            "vulnerability",
            "vulnerabilities",
            "security incident",
            "threat",
            "attack",
            "firewall",
            "vpn",
        ],

        "Data & AI": [
            "data pipeline",
            "data engineering",
            "machine learning",
            "machine learning model",
            "ml model",
            "artificial intelligence",
            "ai model",
            "llm",
            "large language model",
            "embedding",
            "embeddings",
            "vector",
            "vector database",
            "pinecone",
            "rag",
            "retrieval",
            "reranking",
            "analytics",
            "dataset",
            "model training",
            "inference",
        ],
    }


    # -----------------------------------------------------
    # Security gets priority for security-specific terms
    # -----------------------------------------------------

    security_terms = capability_keywords["Security"]

    if any(term in q for term in security_terms):
        return "Security"


    # -----------------------------------------------------
    # Check remaining capabilities
    # -----------------------------------------------------

    for capability, terms in capability_keywords.items():

        if capability == "Security":
            continue

        if any(term in q for term in terms):
            return capability


    return None


# =========================================================
# ENGINEERING AGENT
# =========================================================

def engineering_agent(
    question: str,
    capability: str | None = None,
) -> dict:
    """
    Process an Engineering question using
    the appropriate Engineering capability.
    """

    if not question or not question.strip():

        return {
            "answer": "Please provide an Engineering question.",
            "domain": "Engineering",
            "capability": capability,
            "agent": "engineering",
            "path": "engineering",
            "citations": [],
            "confidence": 0.0,
        }


    question = question.strip()


    # -----------------------------------------------------
    # Detect capability
    # -----------------------------------------------------

    detected_capability = (
        capability
        if capability in ENGINEERING_CAPABILITIES
        else detect_engineering_capability(question)
    )


    # -----------------------------------------------------
    # Default capability
    # -----------------------------------------------------

    if not detected_capability:

        detected_capability = "Code Intelligence"


    # -----------------------------------------------------
    # Capability-specific instructions
    # -----------------------------------------------------

    capability_instructions = {

        "Code Intelligence": (
            "Focus on source code, repositories, services, "
            "dependencies, APIs, implementations and code structure."
        ),

        "Architecture": (
            "Focus on system architecture, components, "
            "service boundaries, data flow and technical design."
        ),

        "QA & Testing": (
            "Focus on testing strategy, test cases, defects, "
            "coverage, quality and validation."
        ),

        "DevOps & Platform": (
            "Focus on deployment, infrastructure, CI/CD, "
            "platform engineering, cloud and production systems."
        ),

        "Security": (
            "Focus on authentication, authorization, identity, "
            "permissions, credentials, vulnerabilities, encryption "
            "and security controls."
        ),

        "Data & AI": (
            "Focus on data pipelines, machine learning, AI, "
            "LLMs, embeddings, retrieval, analytics and models."
        ),
    }


    instruction = capability_instructions[
        detected_capability
    ]


    # -----------------------------------------------------
    # Build controlled RAG prompt
    # -----------------------------------------------------

    enhanced_question = f"""
You are the NEXUS Engineering Agent.

Engineering capability:
{detected_capability}

Your responsibility:
{instruction}

Answer the user's question using ONLY the authorized
company knowledge and retrieved document context.

IMPORTANT RULES:

1. Do NOT reveal your internal reasoning.
2. Do NOT output a "thinking process".
3. Do NOT output analysis steps.
4. Do NOT describe how you searched the documents.
5. Return ONLY the final answer intended for the user.
6. Do NOT invent company-specific facts.
7. If the required information is not present in the
   retrieved context, clearly state that the information
   is not available in the provided documents.
8. Be technically precise and concise.

User question:
{question}
"""


    # -----------------------------------------------------
    # Existing RAG
    # -----------------------------------------------------

    result = answer_question(
        enhanced_question.strip()
    )


    # -----------------------------------------------------
    # Normalize metadata
    # -----------------------------------------------------

    result["domain"] = "Engineering"

    result["capability"] = detected_capability

    result["agent"] = "engineering"

    return result