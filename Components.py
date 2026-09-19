"""
NEXUS - Shared UI components for the multipage app.

app.py (the "All Domains" command center) and every file in pages/
import from here. This is the ONLY place the Streamlit UI is defined:
one CSS theme, one sidebar, one ask/result flow. A domain page is just
a few lines that call these functions with its own domain name -- see
pages/1_Engineering.py for the pattern.

Nothing here talks to rag.py/graph.py directly. It only calls the
FastAPI endpoints (/ask, /upload), exactly like the original
single-page app.py did.
"""

import os
import requests
import streamlit as st
from textwrap import dedent

from Agents.domain_config import DOMAIN_REGISTRY


# =========================================================
# API CONFIGURATION
# =========================================================

API_URL = os.getenv("NEXUS_API_URL", "http://localhost:8000/ask")
UPLOAD_URL = os.getenv("NEXUS_UPLOAD_URL", "http://localhost:8000/upload")
DOCUMENTS_URL = os.getenv("NEXUS_DOCUMENTS_URL", "http://localhost:8000/documents")
ACTION_URL = os.getenv("NEXUS_ACTION_URL", "http://localhost:8000/domain-action")
DASHBOARD_URL = os.getenv("NEXUS_DASHBOARD_URL", "http://localhost:8000/domain-dashboard")


# =========================================================
# DOMAIN DISPLAY METADATA
# (icons + which page file each domain lives on)
# =========================================================

DOMAIN_ICONS = {
    "Engineering": "⌘",
    "Product": "◇",
    "People / HR": "♙",
    "Finance": "◈",
    "Legal & Compliance": "§",
}

DOMAIN_PAGES = {
    "Engineering": "pages/1_Engineering.py",
    "Product": "pages/2_Product.py",
    "People / HR": "pages/3_People_HR.py",
    "Finance": "pages/4_Finance.py",
    "Legal & Compliance": "pages/5_Legal_Compliance.py",
}


# =========================================================
# PAGE SETUP
# =========================================================

def configure_page(title: str):
    """Call this first, before anything else, on every page."""
    st.set_page_config(
        page_title=f"NEXUS · {title}",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def init_session_state():
    if "selected_capability" not in st.session_state:
        st.session_state.selected_capability = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    if "last_responses" not in st.session_state:
        st.session_state.last_responses = {}

    if "domain_action_results" not in st.session_state:
        st.session_state.domain_action_results = {}

    if "domain_dashboard_results" not in st.session_state:
        st.session_state.domain_dashboard_results = {}


# =========================================================
# GLOBAL CSS  (identical theme on every page)
# =========================================================

def inject_css():
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
           AI INSIGHTS DASHBOARD
           ===================================================== */

        .insights-shell {
            background-color: #0f1318;
            border: 1px solid #242a32;
            border-radius: 14px;
            padding: 20px;
            margin-top: 12px;
        }

        .insights-status {
            color: #68717e;
            font-size: 10px;
            margin-bottom: 16px;
        }

        .insight-card {
            background-color: #11151a;
            border: 1px solid #242a32;
            border-radius: 11px;
            padding: 16px;
            min-height: 130px;
        }

        .insight-card-title {
            color: #dfe3e8;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 9px;
        }

        .insight-unavailable {
            color: #59626e;
            font-size: 11px;
            line-height: 1.5;
        }

        .insight-item {
            color: #b8c0ca;
            font-size: 11px;
            line-height: 1.55;
            margin: 6px 0;
        }

        .insight-badge {
            display: inline-block;
            color: #8d98a6;
            background-color: #181d23;
            border: 1px solid #303640;
            border-radius: 20px;
            padding: 4px 8px;
            font-size: 8px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }

        .dashboard-facts {
            border-left: 2px solid #596575;
            padding-left: 14px;
        }

        .dashboard-ai {
            border-left: 2px solid #8a8060;
            padding-left: 14px;
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


        .document-row {
            display: flex;
            align-items: center;
            gap: 12px;
            background-color: #11151a;
            border: 1px solid #242a32;
            border-radius: 10px;
            padding: 13px 15px;
            margin-top: 8px;
        }

        .document-icon {
            font-size: 18px;
            width: 28px;
        }

        .document-info {
            flex: 1;
            min-width: 0;
        }

        .document-name {
            color: #dfe3e8;
            font-size: 12px;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .document-meta {
            color: #68717e;
            font-size: 9px;
            margin-top: 4px;
        }

        .document-status {
            font-size: 10px;
            font-weight: 600;
            text-align: right;
        }

        .document-status-indexed { color: #6ee7a0; }
        .document-status-processing { color: #d8c27a; }
        .document-status-failed { color: #e88a8a; }
        .document-status-unknown { color: #9da6b2; }

        .document-chunks {
            display: block;
            color: #59626e;
            font-size: 8px;
            font-weight: 400;
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


        /* =====================================================
           HIDE DEFAULT MULTIPAGE NAV
           (we render our own with st.page_link so the sidebar
           keeps its original look across every page)
           ===================================================== */

        div[data-testid="stSidebarNav"] {
            display: none;
        }

            </style>
        """),
        unsafe_allow_html=True,
    )

# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar(active_domain: str):
    """
    active_domain: "All Domains" (on app.py) or one of the
    DOMAIN_REGISTRY keys (on a page in pages/).
    """

    with st.sidebar:

        st.markdown('<div class="brand-title">NEXUS</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="brand-subtitle">Enterprise AI Intelligence</div>',
            unsafe_allow_html=True,
        )

        # -----------------------------------------------------
        # DOMAIN NAVIGATION
        # st.page_link auto-highlights whichever page is active,
        # so there's no manual on/off button logic to maintain.
        # -----------------------------------------------------

        st.markdown('<div class="sidebar-title">Domain Agents</div>', unsafe_allow_html=True)

        st.page_link("app.py", label="All Domains", icon="▦")

        for domain, page_path in DOMAIN_PAGES.items():
            st.page_link(page_path, label=domain, icon=DOMAIN_ICONS[domain])

        # -----------------------------------------------------
        # CAPABILITIES (only on a domain-specific page)
        # -----------------------------------------------------

        if active_domain != "All Domains":

            st.markdown(
                '<div class="capabilities">'
                '<div class="capability-title">Capabilities</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            for capability in DOMAIN_REGISTRY[active_domain]["capabilities"]:

                if st.button(
                    f"▹   {capability}",
                    key=f"cap_{active_domain}_{capability}",
                    use_container_width=True,
                ):
                    st.session_state.selected_capability = capability
                    st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # -----------------------------------------------------
        # INTEGRATIONS
        # -----------------------------------------------------

        st.markdown('<div class="sidebar-title">Integrations</div>', unsafe_allow_html=True)

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
                else '<span class="planned">●</span>'
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

        st.markdown('<div class="sidebar-title">Knowledge Ingestion</div>', unsafe_allow_html=True)

        render_upload_widget(active_domain)

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
# UPLOAD WIDGET
# (same logic on every page -- the only thing that changes
# is which domain gets stamped onto the uploaded document)
# =========================================================

def render_upload_widget(active_domain: str):

    uploaded_file = st.file_uploader(
        "Upload knowledge document",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
        key=f"uploader_{active_domain}",
        help="Supported: PDF, TXT, DOCX and common image formats. Images are OCR processed.",
    )

    if not uploaded_file:
        return

    if active_domain != "All Domains":
        st.caption(f"Will be indexed under: **{active_domain}**")
    else:
        st.caption(
            "Will be indexed as a **General** document, "
            "visible to every domain."
        )

    if st.button(
        "Index Document",
        use_container_width=True,
        key=f"index_btn_{active_domain}",
    ):

        with st.spinner("Indexing document..."):

            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                }

                form_data = (
                    {"domain": active_domain}
                    if active_domain != "All Domains"
                    else {}
                )

                response = requests.post(
                    UPLOAD_URL,
                    files=files,
                    data=form_data,
                    timeout=300,
                )

                if response.status_code == 200:
                    indexed_domain = response.json().get("domain", "General")
                    st.success(f"Indexed: {uploaded_file.name} → {indexed_domain}")

                else:
                    try:
                        detail = response.json().get("detail", "Unknown error")
                    except ValueError:
                        detail = "Unknown error"
                    st.error(f"Upload failed: {detail}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to NEXUS backend.")

            except requests.exceptions.Timeout:
                st.error("Upload timed out.")

            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {e}")


# =========================================================
# MAIN DOCUMENT UPLOAD
# =========================================================

def render_domain_upload_section(active_domain: str):
    """Render the document ingestion area inside every domain workspace."""

    st.markdown('<div class="section-label">KNOWLEDGE INGESTION</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="ask-title">Add domain knowledge</div>'
        '<div class="ask-description">'
        'Upload documents or images for this domain. PDF, TXT and DOCX files are '
        'indexed directly; images are passed through OCR before indexing.'
        '</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "webp"],
        key=f"main_upload_{active_domain}",
        help="Images use OCR. Legacy .doc files are not supported; save them as .docx.",
    )

    if uploaded_file is None:
        return

    col1, col2 = st.columns([4, 1])

    with col1:
        st.caption(f"Selected: **{uploaded_file.name}** · {uploaded_file.size / 1024:.1f} KB")

    with col2:
        index_clicked = st.button(
            "Index Document",
            type="primary",
            use_container_width=True,
            key=f"main_index_{active_domain}",
        )

    if not index_clicked:
        return

    with st.status(
        "Uploading document...",
        expanded=True,
    ) as upload_status:
        try:
            upload_status.update(
                label="Processing document...",
                state="running",
                expanded=True,
            )
            response = requests.post(
                UPLOAD_URL,
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                },
                data={"domain": active_domain},
                timeout=300,
            )

            if response.status_code == 200:
                data = response.json()
                upload_status.update(
                    label="Indexed and ready",
                    state="complete",
                    expanded=False,
                )
                st.success(
                    f"Indexed **{data.get('filename', uploaded_file.name)}** "
                    f"for **{data.get('domain', active_domain)}**."
                )
                if data.get("ocr"):
                    st.info("OCR was used to extract text from the uploaded image.")
            else:
                upload_status.update(
                    label="Indexing failed",
                    state="error",
                    expanded=True,
                )
                try:
                    detail = response.json().get("detail", "Unknown error")
                except ValueError:
                    detail = "Unknown error"
                st.error(f"Upload failed: {detail}")

        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to {UPLOAD_URL}. Make sure FastAPI is running.")
        except requests.exceptions.Timeout:
            st.error("Upload timed out.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Upload failed: {exc}")


# =========================================================
# DOMAIN INTELLIGENCE QUICK ACTIONS
# =========================================================

def render_domain_quick_actions(active_domain: str):
    actions = DOMAIN_REGISTRY.get(active_domain, {}).get("quick_actions", [])
    if not actions:
        return
    st.markdown('<div class="section-label">DOMAIN INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="ask-title">Quick Actions</div><div class="ask-description">Run a grounded workflow over documents indexed for this domain.</div>', unsafe_allow_html=True)
    columns = st.columns(min(3, len(actions)))
    for index, (label, description) in enumerate(actions):
        with columns[index % len(columns)]:
            st.markdown(f'<div class="quick-card"><div class="quick-icon">◇</div><div class="quick-name">{label}</div><div class="quick-description">{description}</div></div>', unsafe_allow_html=True)
            if st.button("Run →", key=f"action_{active_domain}_{label}", use_container_width=True):
                with st.spinner(f"Running {label}..."):
                    try:
                        response = requests.post(ACTION_URL, json={"domain": active_domain, "action": label}, timeout=120)
                        if response.status_code != 200:
                            try: detail = response.json().get("detail", "Unknown error")
                            except ValueError: detail = "Unknown error"
                            st.error(f"Action failed: {detail}")
                        else:
                            st.session_state.domain_action_results[active_domain] = response.json().get("response", {})
                            st.rerun()
                    except requests.exceptions.ConnectionError: st.error("Cannot connect to NEXUS backend.")
                    except requests.exceptions.Timeout: st.error("The intelligence action timed out.")
                    except requests.exceptions.RequestException as exc: st.error(f"Action failed: {exc}")
    result = st.session_state.domain_action_results.get(active_domain)
    if result:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="result-agent">{result.get("action", "Domain Intelligence")} · grounded result</div>', unsafe_allow_html=True)
        st.markdown(result.get("answer", "No result returned."))
        citations = result.get("citations") or []
        if citations:
            st.caption("Sources")
            for citation in citations:
                source = citation.get("source", "Unknown source")
                page = citation.get("page_number")
                st.markdown(f"- {source} · p.{page}" if page else f"- {source}")
        confidence = result.get("confidence")
        if confidence is not None:
            try: st.caption(f"Confidence {float(confidence):.2f}")
            except (ValueError, TypeError): pass
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

def render_header(active_domain: str):

    if active_domain == "All Domains":

        st.markdown('<div class="eyebrow">NEXUS COMMAND CENTER</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-title">Good afternoon, Pari</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="main-description">'
            'Enterprise knowledge, intelligence and action — unified.'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        capability = st.session_state.selected_capability
        title = capability if capability else active_domain

        st.markdown('<div class="eyebrow">DOMAIN AGENT</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="main-description">'
            f'Permission-aware intelligence for the {active_domain} domain.'
            f'</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# METRICS  (static placeholders, same as the original)
# =========================================================

def render_metrics():

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
# ASK + RESULT
# =========================================================

def render_document_library(active_domain: str):
    """Render the persisted Pinecone-backed document library for one domain."""
    st.markdown('<div class="section-label">DOCUMENT LIBRARY</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ask-title">{active_domain.upper()} DOCUMENTS</div>',
        unsafe_allow_html=True,
    )

    try:
        response = requests.get(
            DOCUMENTS_URL,
            params={"domain": active_domain},
            timeout=30,
        )
    except requests.exceptions.ConnectionError:
        st.info("Document library is unavailable because the NEXUS backend is offline.")
        return
    except requests.exceptions.Timeout:
        st.warning("Document library request timed out.")
        return
    except requests.exceptions.RequestException as exc:
        st.error(f"Document library failed: {exc}")
        return

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", "Unknown error")
        except ValueError:
            detail = "Unknown error"
        st.error(f"Could not load document library: {detail}")
        return

    records = response.json().get("documents", [])

    if not records:
        st.markdown(
            '<div class="activity-card"><div class="activity-row">'
            '<div class="activity-name">No documents indexed yet</div>'
            '<div class="activity-meta">Upload a PDF, TXT, DOCX or image to build this domain knowledge base.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        return

    for record in records:
        filename = record.get("filename", "Unknown")
        domain = record.get("domain", active_domain)
        file_type = str(record.get("file_type", "unknown")).upper()
        status = str(record.get("status", "unknown")).lower()
        ocr = record.get("ocr", False)
        indexed = record.get("indexed", False)
        created_at = record.get("created_at") or "Unknown time"
        chunks = record.get("chunk_count", 0)

        status_label = {
            "indexed": "Indexed",
            "processing": "Processing",
            "failed": "Failed",
        }.get(status, status.title())

        icon = "🖼️" if ocr else "📄"
        ocr_label = " · OCR" if ocr else ""
        indexed_label = " · Ready" if indexed and status == "indexed" else ""

        st.markdown(
            f'<div class="document-row">'
            f'<div class="document-icon">{icon}</div>'
            f'<div class="document-info">'
            f'<div class="document-name">{filename}</div>'
            f'<div class="document-meta">{domain} · {file_type}{ocr_label} · {created_at}</div>'
            f'</div>'
            f'<div class="document-status document-status-{status}">{status_label}{indexed_label}'
            f'<span class="document-chunks">{chunks} chunks</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if status == "failed" and record.get("error"):
            st.caption(f"Failure: {record['error']}")


def _render_chat_message(item: dict):
    question = item.get("question", "")
    response = item.get("response", {})
    answer = response.get("answer", "No answer returned.")
    citations = response.get("citations") or []
    confidence = response.get("confidence")

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        st.markdown(answer)

        if citations:
            st.caption("Sources")
            for citation in citations:
                source = citation.get("source", "Unknown source")
                page = citation.get("page_number")
                label = f"{source} · p.{page}" if page else source
                st.markdown(f"- {label}")

        if confidence is not None:
            try:
                st.caption(f"Confidence {float(confidence):.2f}")
            except (ValueError, TypeError):
                pass


def render_ask_and_result(active_domain: str):
    """Render a persistent, domain-scoped conversation using the existing /ask API."""
    st.markdown('<div class="section-label">NEXUS INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ask-title">What do you need to understand?</div>'
        '<div class="ask-description">'
        'Ask follow-up questions while staying inside this domain knowledge boundary.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Only replay messages belonging to the current domain.
    domain_messages = (
        st.session_state.messages
        if active_domain == "All Domains"
        else [
            item for item in st.session_state.messages
            if item.get("domain") == active_domain
        ]
    )

    for item in domain_messages:
        _render_chat_message(item)

    query = st.chat_input(
        f"Ask the {active_domain} agent...",
        key=f"chat_input_{active_domain}",
    )

    if not query:
        return

    if not query.strip():
        st.warning("Enter a question first.")
        return

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("NEXUS is routing, retrieving and grounding the answer..."):
            try:
                payload = {
                    "query": query,
                    "domain": None if active_domain == "All Domains" else active_domain,
                    "capability": st.session_state.selected_capability,
                }

                response = requests.post(API_URL, json=payload, timeout=60)

                if response.status_code != 200:
                    try:
                        detail = response.json().get("detail", "No detail provided.")
                    except ValueError:
                        detail = "No response body."
                    st.error(f"Backend returned {response.status_code}: {detail}")
                    return

                data = response.json()
                result = data.get("response", data)
                result_domain = result.get("domain", active_domain)

                st.session_state.last_response = result
                st.session_state.last_responses[active_domain] = result
                st.session_state.messages.append({
                    "question": query,
                    "response": result,
                    "domain": result_domain,
                })

                st.markdown(result.get("answer", "No answer returned."))

                citations = result.get("citations") or []
                if citations:
                    st.caption("Sources")
                    for citation in citations:
                        source = citation.get("source", "Unknown source")
                        page = citation.get("page_number")
                        label = f"{source} · p.{page}" if page else source
                        st.markdown(f"- {label}")

                confidence = result.get("confidence")
                if confidence is not None:
                    try:
                        st.caption(f"Confidence {float(confidence):.2f}")
                    except (ValueError, TypeError):
                        pass

            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to {API_URL}. Make sure FastAPI is running.")
            except requests.exceptions.Timeout:
                st.error("The request timed out.")
            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")




# =========================================================
# QUICK ACCESS  (only shown on the "All Domains" page)
# =========================================================

def render_quick_access():

    st.markdown('<div class="section-label">QUICK ACCESS</div>', unsafe_allow_html=True)

    columns = st.columns(len(DOMAIN_PAGES))

    for column, (domain, page_path) in zip(columns, DOMAIN_PAGES.items()):

        with column:
            st.markdown(
                '<div class="quick-card">'
                f'<div class="quick-icon">{DOMAIN_ICONS[domain]}</div>'
                f'<div class="quick-name">{domain}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page_path, label="Open →", icon=None)


# =========================================================
# RECENT ACTIVITY
# =========================================================

def render_recent_activity():

    st.markdown('<div class="section-label">RECENT ACTIVITY</div>', unsafe_allow_html=True)

    if st.session_state.messages:

        activity_html = '<div class="activity-card">'

        for item in reversed(st.session_state.messages[-5:]):

            question_text = item["question"]
            response_data = item["response"]
            activity_domain = response_data.get("domain", "NEXUS")

            activity_html += (
                '<div class="activity-row">'
                f'<div class="activity-name">{question_text}</div>'
                f'<div class="activity-meta">{activity_domain}</div>'
                '</div>'
            )

        activity_html += "</div>"

        st.markdown(activity_html, unsafe_allow_html=True)

    else:

        st.markdown(
            '<div class="activity-card">'
            '<div class="activity-row">'
            '<div class="activity-name">No recent activity</div>'
            '<div class="activity-meta">Your NEXUS queries will appear here.</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# ONE-CALL PAGE RENDER
# (what every file in pages/ actually calls)
# =========================================================

def render_domain_workspace(domain: str):
    """
    Renders a full domain page: sidebar + header + metrics + ask/result.
    Every file in pages/ is just:

        from components import configure_page, init_session_state, render_domain_workspace
        configure_page("Finance")
        init_session_state()
        render_domain_workspace("Finance")
    """

    init_session_state()
    inject_css()
    render_sidebar(domain)
    render_header(domain)
    render_metrics()
    render_domain_dashboard(domain)
    render_domain_quick_actions(domain)
    render_domain_upload_section(domain)
    render_document_library(domain)
    render_ask_and_result(domain)