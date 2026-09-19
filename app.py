import os
import requests
import streamlit as st
from textwrap import dedent


# =========================================================
# NEXUS — ENTERPRISE AI INTELLIGENCE PLATFORM
# REAL FRONTEND
# =========================================================

st.set_page_config(
    page_title="NEXUS",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# API CONFIGURATION
# =========================================================

API_URL = os.getenv(
    "NEXUS_API_URL",
    "http://localhost:8000/ask"
)

UPLOAD_URL = os.getenv(
    "NEXUS_UPLOAD_URL",
    "http://localhost:8000/upload"
)


# =========================================================
# SESSION STATE
# =========================================================

if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = "All Domains"

if "selected_capability" not in st.session_state:
    st.session_state.selected_capability = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response" not in st.session_state:
    st.session_state.last_response = None


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    dedent("""
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background-color: #0b0d10;
        color: #e8eaed;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-left: 3.5rem;
        padding-right: 3.5rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background-color: #0b0d10;
    }

    footer {
        visibility: hidden;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background-color: #101318;
        border-right: 1px solid #242830;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0.8rem;
        padding-left: 0.55rem;
        padding-right: 0.55rem;
    }


    /* =====================================================
       BRAND
       ===================================================== */

    .brand-title {
        color: #f5f7fa;
        font-size: 25px;
        font-weight: 800;
        letter-spacing: 0.22em;
        margin-left: 9px;
        margin-top: 5px;
    }

    .brand-subtitle {
        color: #68717e;
        font-size: 9px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-left: 10px;
        margin-top: 6px;
        margin-bottom: 30px;
    }


    /* =====================================================
       SIDEBAR TITLES
       ===================================================== */

    .sidebar-title {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-left: 10px;
        margin-top: 15px;
        margin-bottom: 9px;
    }


    /* =====================================================
       SIDEBAR BUTTONS
       ===================================================== */

    section[data-testid="stSidebar"] .stButton {
        margin: 0;
        padding: 0;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 40px;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        color: #b8c0ca;
        font-size: 13px;
        font-weight: 500;
        text-align: left;
        padding: 8px 12px;
        margin-bottom: 2px;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #191d23;
        border-color: #292f37;
        color: #f5f7fa;
    }


    /* =====================================================
       ACTIVE DOMAIN
       ===================================================== */

    .active-domain {
        width: 100%;
        min-height: 40px;
        box-sizing: border-box;

        display: flex;
        align-items: center;

        background-color: #1a1f26;
        border: 1px solid #303640;
        border-radius: 8px;

        color: #f5f7fa;

        font-size: 13px;
        font-weight: 600;

        padding: 8px 12px;
        margin-bottom: 2px;
    }

    .active-icon {
        width: 27px;
        color: #aab3bf;
    }

    .active-name {
        flex: 1;
    }

    .active-arrow {
        color: #89929e;
    }


    /* =====================================================
       CAPABILITIES
       ===================================================== */

    .capabilities {
        margin-left: 14px;
        padding-left: 13px;
        border-left: 1px solid #303640;
        margin-top: 4px;
        margin-bottom: 7px;
    }

    .capability-title {
        color: #59626e;
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        padding: 6px 7px;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    .sidebar-divider {
        height: 1px;
        background-color: #242830;
        margin: 20px 8px 18px 8px;
    }


    /* =====================================================
       INTEGRATIONS
       ===================================================== */

    .integration-row {
        display: flex;
        align-items: center;

        min-height: 36px;

        padding: 6px 10px;

        border-radius: 7px;

        color: #aeb6c1;

        font-size: 12px;
    }

    .integration-icon {
        width: 28px;
        color: #808a97;
    }

    .integration-name {
        flex: 1;
    }

    .connected {
        color: #6ee7a0;
        font-size: 8px;
    }

    .planned {
        color: #4b5563;
        font-size: 8px;
    }


    /* =====================================================
       USER
       ===================================================== */

    .user-card {
        display: flex;
        align-items: center;

        background-color: #15191f;

        border: 1px solid #303640;
        border-radius: 8px;

        padding: 9px;

        margin: 18px 7px 5px 7px;
    }

    .avatar {
        width: 32px;
        height: 32px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background-color: #2c333c;

        color: #f5f7fa;

        font-size: 13px;
        font-weight: 600;

        margin-right: 9px;
    }

    .user-info {
        flex: 1;
    }

    .user-name {
        color: #e8eaed;
        font-size: 11px;
        font-weight: 600;
    }

    .user-team {
        color: #68717e;
        font-size: 9px;
        margin-top: 2px;
    }

    .online {
        width: 7px;
        height: 7px;
        background-color: #6ee7a0;
        border-radius: 50%;
    }


    /* =====================================================
       MAIN HEADER
       ===================================================== */

    .eyebrow {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.17em;
        text-transform: uppercase;
        margin-bottom: 9px;
    }

    .main-title {
        color: #f5f7fa;
        font-size: 40px;
        font-weight: 600;
        letter-spacing: -0.04em;
        margin-bottom: 6px;
    }

    .main-description {
        color: #747d8a;
        font-size: 13px;
        margin-bottom: 28px;
    }


    /* =====================================================
       METRICS
       ===================================================== */

    .metric-card {
        background-color: #11151a;
        border: 1px solid #242a32;
        border-radius: 12px;
        padding: 17px;
        min-height: 105px;
    }

    .metric-label {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.09em;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #f5f7fa;
        font-size: 27px;
        font-weight: 600;
    }

    .metric-meta {
        color: #68717e;
        font-size: 9px;
        margin-top: 6px;
    }


    /* =====================================================
       ASK AREA
       ===================================================== */

    .section-label {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 30px;
        margin-bottom: 9px;
    }

    .ask-title {
        color: #e8eaed;
        font-size: 19px;
        font-weight: 500;
        margin-bottom: 4px;
    }

    .ask-description {
        color: #68717e;
        font-size: 11px;
        margin-bottom: 12px;
    }


    /* =====================================================
       INPUT
       ===================================================== */

    div[data-testid="stTextInput"] input {
        background-color: #11151a !important;
        border: 1px solid #303640 !important;
        border-radius: 11px !important;
        color: #e8eaed !important;
        height: 50px !important;
        font-size: 13px !important;
        padding-left: 17px !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #59626e !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #596575 !important;
        box-shadow: none !important;
    }


    /* =====================================================
       QUICK ACCESS
       ===================================================== */

    .quick-card {
        background-color: #11151a;
        border: 1px solid #242a32;
        border-radius: 10px;
        padding: 15px;
        min-height: 88px;
    }

    .quick-icon {
        color: #9ca6b3;
        font-size: 17px;
        margin-bottom: 7px;
    }

    .quick-name {
        color: #dfe3e8;
        font-size: 12px;
        font-weight: 500;
    }

    .quick-description {
        color: #68717e;
        font-size: 9px;
        margin-top: 4px;
    }


    /* =====================================================
       RESULT
       ===================================================== */

    .result-card {
        background-color: #11151a;
        border: 1px solid #303640;
        border-radius: 12px;
        padding: 22px;
        margin-top: 25px;
    }

    .result-agent {
        color: #68717e;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 12px;
    }

    .result-answer {
        color: #e8eaed;
        font-size: 15px;
        line-height: 1.65;
    }

    .citation {
        display: inline-block;
        background-color: #181d23;
        border: 1px solid #303640;
        border-radius: 7px;
        padding: 5px 9px;
        margin: 5px 5px 0 0;
        color: #9da6b2;
        font-size: 10px;
    }

    .confidence {
        display: inline-block;
        margin-top: 14px;
        padding: 5px 10px;
        border-radius: 20px;
        background-color: #18241e;
        color: #6ee7a0;
        font-size: 10px;
        font-weight: 600;
    }


    /* =====================================================
       ACTIVITY
       ===================================================== */

    .activity-card {
        background-color: #11151a;
        border: 1px solid #242a32;
        border-radius: 11px;
        overflow: hidden;
    }

    .activity-row {
        padding: 14px 17px;
        border-bottom: 1px solid #20252c;
    }

    .activity-row:last-child {
        border-bottom: none;
    }

    .activity-name {
        color: #dfe3e8;
        font-size: 11px;
        font-weight: 500;
    }

    .activity-meta {
        color: #68717e;
        font-size: 9px;
        margin-top: 3px;
    }


    /* =====================================================
       UPLOAD
       ===================================================== */

    .upload-box {
        background-color: #11151a;
        border: 1px solid #242a32;
        border-radius: 11px;
        padding: 18px;
        margin-top: 20px;
    }

    </style>
    """),
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="brand-title">NEXUS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="brand-subtitle">'
        'Enterprise AI Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # DOMAIN AGENTS
    # -----------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">Domain Agents</div>',
        unsafe_allow_html=True,
    )


    domains = [
        ("▦", "All Domains"),
        ("⌘", "Engineering"),
        ("◇", "Product"),
        ("♙", "People / HR"),
        ("◈", "Finance"),
        ("§", "Legal & Compliance"),
    ]


    for icon, domain in domains:

        if domain == "Engineering":

            if st.session_state.selected_domain == "Engineering":

                st.markdown(
                    '<div class="active-domain">'
                    '<span class="active-icon">⌘</span>'
                    '<span class="active-name">Engineering</span>'
                    '<span class="active-arrow">⌃</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="capabilities">'
                    '<div class="capability-title">'
                    'Capabilities'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )


                capabilities = [
                    ("⌘", "Code Intelligence"),
                    ("▤", "Architecture"),
                    ("✓", "QA & Testing"),
                    ("◉", "Data & AI"),
                    ("◈", "DevOps & Security"),
                ]


                for cap_icon, capability in capabilities:

                    if st.button(
                        f"{cap_icon}   {capability}",
                        key=f"cap_{capability}",
                        use_container_width=True,
                    ):

                        st.session_state.selected_capability = capability
                        st.rerun()

            else:

                if st.button(
                    "⌘   Engineering",
                    key="domain_engineering",
                    use_container_width=True,
                ):

                    st.session_state.selected_domain = "Engineering"
                    st.session_state.selected_capability = None
                    st.rerun()

        else:

            if st.session_state.selected_domain == domain:

                st.markdown(
                    f'<div class="active-domain">'
                    f'<span class="active-icon">{icon}</span>'
                    f'<span class="active-name">{domain}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            else:

                if st.button(
                    f"{icon}   {domain}",
                    key=f"domain_{domain}",
                    use_container_width=True,
                ):

                    st.session_state.selected_domain = domain
                    st.session_state.selected_capability = None
                    st.rerun()


    # -----------------------------------------------------
    # DIVIDER
    # -----------------------------------------------------

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # INTEGRATIONS
    # -----------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">Integrations</div>',
        unsafe_allow_html=True,
    )


    integrations = [
        ("◉", "GitHub", True),
        ("⌁", "VS Code Context", True),
        ("▧", "OCR Pipeline", True),
        ("◇", "Jira", False),
    ]


    for icon, name, connected in integrations:

        status = (
            '<span class="connected">●</span>'
            if connected
            else
            '<span class="planned">●</span>'
        )

        st.markdown(
            '<div class="integration-row">'
            f'<span class="integration-icon">{icon}</span>'
            f'<span class="integration-name">{name}</span>'
            f'{status}'
            '</div>',
            unsafe_allow_html=True,
        )


    # -----------------------------------------------------
    # UPLOAD
    # -----------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">Knowledge Ingestion</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file:

        if st.button(
            "Index Document",
            use_container_width=True,
        ):

            with st.spinner("Indexing document..."):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }

                    response = requests.post(
                        UPLOAD_URL,
                        files=files,
                        timeout=300,
                    )

                    if response.status_code == 200:

                        st.success(
                            f"Indexed: {uploaded_file.name}"
                        )

                    else:

                        try:
                            detail = response.json().get(
                                "detail",
                                "Unknown error"
                            )
                        except ValueError:
                            detail = "Unknown error"

                        st.error(
                            f"Upload failed: {detail}"
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to NEXUS backend."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Upload timed out."
                    )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Upload failed: {e}"
                    )


    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    st.markdown(
        '<div class="user-card">'
        '<div class="avatar">P</div>'
        '<div class="user-info">'
        '<div class="user-name">Pari</div>'
        '<div class="user-team">Engineering Team</div>'
        '</div>'
        '<div class="online"></div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN WORKSPACE
# =========================================================

selected_domain = st.session_state.selected_domain
selected_capability = st.session_state.selected_capability


# =========================================================
# HEADER
# =========================================================

if selected_domain == "All Domains":

    st.markdown(
        '<div class="eyebrow">NEXUS COMMAND CENTER</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-title">'
        'Good afternoon, Pari'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-description">'
        'Enterprise knowledge, intelligence and action — unified.'
        '</div>',
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        '<div class="eyebrow">DOMAIN AGENT</div>',
        unsafe_allow_html=True,
    )

    title = (
        selected_capability
        if selected_capability
        else selected_domain
    )

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="main-description">'
        f'Permission-aware intelligence for the '
        f'{selected_domain} domain.'
        f'</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# METRICS
# =========================================================

m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">QUERIES TODAY</div>'
        '<div class="metric-value">341</div>'
        '<div class="metric-meta">↑ 12% from yesterday</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with m2:

    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">GROUNDING RATE</div>'
        '<div class="metric-value">96.4%</div>'
        '<div class="metric-meta">High answer reliability</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with m3:

    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">DOCUMENTS IN OCR</div>'
        '<div class="metric-value">7</div>'
        '<div class="metric-meta">Processing queue</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with m4:

    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">STALE EMBEDDINGS</div>'
        '<div class="metric-value">4</div>'
        '<div class="metric-meta">Re-index recommended</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# ASK NEXUS
# =========================================================

st.markdown(
    '<div class="section-label">NEXUS INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ask-title">'
    'What do you need to understand?'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ask-description">'
    'Ask across your authorized company knowledge, '
    'systems and connected tools.'
    '</div>',
    unsafe_allow_html=True,
)


query = st.text_input(
    "Ask NEXUS",
    placeholder="Ask NEXUS anything...",
    label_visibility="collapsed",
)


ask = st.button(
    "Ask NEXUS",
    type="primary",
)


# =========================================================
# QUERY HANDLING
# =========================================================

if ask:

    if not query.strip():

        st.warning("Enter a question first.")

    else:

        with st.spinner(
            "NEXUS is routing your question..."
        ):

            try:

                payload = {
                    "query": query
                }

                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=60,
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    f"Cannot connect to {API_URL}. "
                    "Make sure FastAPI is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Request failed: {e}"
                )

            else:

                if response.status_code == 200:

                    data = response.json()

                    result = data.get(
                        "response",
                        data
                    )

                    st.session_state.last_response = result

                    st.session_state.messages.append(
                        {
                            "question": query,
                            "response": result,
                        }
                    )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            "No detail provided."
                        )

                    except ValueError:

                        detail = "No response body."

                    st.error(
                        f"Backend returned "
                        f"{response.status_code}: {detail}"
                    )


# =========================================================
# RESULT
# =========================================================

result = st.session_state.last_response


if result:

    st.markdown(
        '<div class="section-label">NEXUS RESPONSE</div>',
        unsafe_allow_html=True,
    )

    agent = result.get(
        "agent",
        "unknown"
    )

    domain = result.get(
        "domain",
        selected_domain
    )

    capability = result.get(
        "capability"
    )

    answer = result.get(
        "answer",
        "No answer returned."
    )

    path = result.get(
        "path",
        "unknown"
    )


    agent_label = domain

    if capability:

        agent_label += (
            f" · {capability}"
        )


    st.markdown(
        '<div class="result-card">'
        f'<div class="result-agent">'
        f'{agent_label} · {path}'
        f'</div>'
        f'<div class="result-answer">'
        f'{answer}'
        f'</div>'
        '</div>',
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # CITATIONS
    # -----------------------------------------------------

    citations = result.get(
        "citations"
    ) or []


    if citations:

        st.markdown(
            '<div class="section-label">'
            'SOURCES'
            '</div>',
            unsafe_allow_html=True,
        )

        citation_html = ""

        for citation in citations:

            source = citation.get(
                "source",
                "Unknown source"
            )

            page = citation.get(
                "page_number"
            )

            label = source

            if page:
                label += f" · p.{page}"

            citation_html += (
                f'<span class="citation">'
                f'📄 {label}'
                f'</span>'
            )


        st.markdown(
            citation_html,
            unsafe_allow_html=True,
        )


    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    confidence = result.get(
        "confidence"
    )

    if confidence is not None:

        try:

            confidence_value = float(
                confidence
            )

            st.markdown(
                f'<span class="confidence">'
                f'✓ Confidence '
                f'{confidence_value:.2f}'
                f'</span>',
                unsafe_allow_html=True,
            )

        except (ValueError, TypeError):

            pass


# =========================================================
# QUICK ACCESS
# =========================================================

st.markdown(
    '<div class="section-label">'
    'QUICK ACCESS'
    '</div>',
    unsafe_allow_html=True,
)


q1, q2, q3, q4 = st.columns(4)


quick_items = [
    (
        q1,
        "⌘",
        "Engineering",
        "Code, architecture & systems",
    ),
    (
        q2,
        "◇",
        "Product",
        "Roadmaps & requirements",
    ),
    (
        q3,
        "◈",
        "Finance",
        "Budgets & financial knowledge",
    ),
    (
        q4,
        "♙",
        "People",
        "Policies & employee knowledge",
    ),
]


for column, icon, name, description in quick_items:

    with column:

        st.markdown(
            '<div class="quick-card">'
            f'<div class="quick-icon">{icon}</div>'
            f'<div class="quick-name">{name}</div>'
            f'<div class="quick-description">'
            f'{description}'
            f'</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# RECENT ACTIVITY
# =========================================================

st.markdown(
    '<div class="section-label">'
    'RECENT ACTIVITY'
    '</div>',
    unsafe_allow_html=True,
)


if st.session_state.messages:

    activity_html = (
        '<div class="activity-card">'
    )

    for item in reversed(
        st.session_state.messages[-5:]
    ):

        question_text = item["question"]

        response_data = item["response"]

        activity_domain = response_data.get(
            "domain",
            "NEXUS"
        )

        activity_html += (
            '<div class="activity-row">'
            f'<div class="activity-name">'
            f'{question_text}'
            f'</div>'
            f'<div class="activity-meta">'
            f'{activity_domain}'
            f'</div>'
            '</div>'
        )

    activity_html += "</div>"

    st.markdown(
        activity_html,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        '<div class="activity-card">'
        '<div class="activity-row">'
        '<div class="activity-name">'
        'No recent activity'
        '</div>'
        '<div class="activity-meta">'
        'Your NEXUS queries will appear here.'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )