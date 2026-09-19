import streamlit as st
from textwrap import dedent


# =========================================================
# NEXUS — ENTERPRISE AI INTELLIGENCE PLATFORM
# FRONTEND FOUNDATION
# =========================================================

st.set_page_config(
    page_title="NEXUS",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = "All Domains"

if "selected_capability" not in st.session_state:
    st.session_state.selected_capability = None


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
        padding-top: 2.2rem;
        padding-left: 3.5rem;
        padding-right: 3.5rem;
        padding-bottom: 3rem;
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
        margin-bottom: 31px;
    }


    /* =====================================================
       SIDEBAR SECTION TITLE
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
       ACTIVE SIDEBAR ITEM
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

    .active-domain-icon {
        width: 27px;
        color: #aab3bf;
        font-size: 14px;
    }

    .active-domain-name {
        flex: 1;
    }

    .active-domain-arrow {
        color: #89929e;
        font-size: 12px;
    }


    /* =====================================================
       ENGINEERING CAPABILITIES
       ===================================================== */

    .capabilities {
        margin-left: 13px;
        padding-left: 13px;
        border-left: 1px solid #303640;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    .capability-label {
        color: #59626e;
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        padding: 7px 8px 5px 8px;
    }

    .capability-button {
        color: #89929e;
        font-size: 12px;
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

    .integration-row:hover {
        background-color: #191d23;
    }

    .integration-icon {
        width: 28px;
        color: #808a97;
        font-size: 13px;
    }

    .integration-name {
        flex: 1;
    }

    .status-connected {
        color: #6ee7a0;
        font-size: 8px;
    }

    .status-planned {
        color: #4b5563;
        font-size: 8px;
    }


    /* =====================================================
       USER CARD
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

    .user-avatar {
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

    .user-online {
        width: 7px;
        height: 7px;
        background-color: #6ee7a0;
        border-radius: 50%;
    }


    /* =====================================================
       MAIN HEADER
       ===================================================== */

    .workspace-eyebrow {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.17em;
        text-transform: uppercase;
        margin-bottom: 9px;
    }

    .workspace-title {
        color: #f5f7fa;
        font-size: 40px;
        font-weight: 600;
        letter-spacing: -0.04em;
        margin-bottom: 6px;
    }

    .workspace-description {
        color: #747d8a;
        font-size: 13px;
        margin-bottom: 29px;
    }


    /* =====================================================
       METRICS
       ===================================================== */

    div[data-testid="stMetric"] {
        background-color: #11151a;
        border: 1px solid #242a32;
        border-radius: 12px;
        padding: 17px;
        min-height: 105px;
    }

    div[data-testid="stMetricLabel"] {
        color: #68717e !important;
        font-size: 9px !important;
        font-weight: 700 !important;
        letter-spacing: 0.09em;
    }

    div[data-testid="stMetricValue"] {
        color: #f5f7fa !important;
        font-size: 27px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 9px !important;
    }


    /* =====================================================
       ASK NEXUS
       ===================================================== */

    .ask-label {
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
       SECTION TITLE
       ===================================================== */

    .section-title {
        color: #68717e;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 29px;
        margin-bottom: 11px;
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
       RECENT ACTIVITY
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

    </style>
    """),
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # =====================================================
    # BRAND
    # =====================================================

    st.markdown(
        '<div class="brand-title">NEXUS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="brand-subtitle">Enterprise AI Intelligence</div>',
        unsafe_allow_html=True,
    )


    # =====================================================
    # DOMAIN AGENTS
    # =====================================================

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

        # =================================================
        # ENGINEERING
        # =================================================

        if domain == "Engineering":

            if st.session_state.selected_domain == "Engineering":

                st.markdown(
                    '<div class="active-domain">'
                    '<span class="active-domain-icon">⌘</span>'
                    '<span class="active-domain-name">Engineering</span>'
                    '<span class="active-domain-arrow">⌃</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )


                # -----------------------------------------
                # ENGINEERING CAPABILITIES
                # -----------------------------------------

                st.markdown(
                    '<div class="capabilities">'
                    '<div class="capability-label">Capabilities</div>'
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
                        key=f"capability_{capability}",
                        use_container_width=True,
                    ):

                        st.session_state.selected_capability = capability
                        st.rerun()


            else:

                if st.button(
                    "⌘   Engineering",
                    key="engineering_button",
                    use_container_width=True,
                ):

                    st.session_state.selected_domain = "Engineering"
                    st.session_state.selected_capability = None
                    st.rerun()


        # =================================================
        # OTHER DOMAINS
        # =================================================

        else:

            if st.session_state.selected_domain == domain:

                st.markdown(
                    f'<div class="active-domain">'
                    f'<span class="active-domain-icon">{icon}</span>'
                    f'<span class="active-domain-name">{domain}</span>'
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


    # =====================================================
    # DIVIDER
    # =====================================================

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )


    # =====================================================
    # INTEGRATIONS
    # =====================================================

    st.markdown(
        '<div class="sidebar-title">Integrations</div>',
        unsafe_allow_html=True,
    )


    integrations = [
        ("◉", "GitHub", "connected"),
        ("⌁", "VS Code Context", "connected"),
        ("▧", "OCR Pipeline", "connected"),
        ("◇", "Jira", "planned"),
    ]


    for icon, name, status in integrations:

        if status == "connected":

            status_html = (
                '<span class="status-connected">●</span>'
            )

        else:

            status_html = (
                '<span class="status-planned">●</span>'
            )


        integration_html = (
            '<div class="integration-row">'
            f'<span class="integration-icon">{icon}</span>'
            f'<span class="integration-name">{name}</span>'
            f'{status_html}'
            '</div>'
        )


        st.markdown(
            integration_html,
            unsafe_allow_html=True,
        )


    # =====================================================
    # USER PROFILE
    # =====================================================

    st.markdown(
        '<div class="user-card">'
        '<div class="user-avatar">P</div>'
        '<div class="user-info">'
        '<div class="user-name">Pari</div>'
        '<div class="user-team">Engineering Team</div>'
        '</div>'
        '<div class="user-online"></div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN WORKSPACE
# =========================================================

selected = st.session_state.selected_domain
capability = st.session_state.selected_capability


# =========================================================
# HEADER
# =========================================================

if selected == "All Domains":

    st.markdown(
        '<div class="workspace-eyebrow">NEXUS COMMAND CENTER</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="workspace-title">Good afternoon, Pari</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="workspace-description">'
        'Enterprise knowledge, intelligence and action — unified.'
        '</div>',
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        '<div class="workspace-eyebrow">DOMAIN AGENT</div>',
        unsafe_allow_html=True,
    )

    page_title = capability if capability else selected

    st.markdown(
        f'<div class="workspace-title">{page_title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="workspace-description">'
        f'Permission-aware intelligence for the {selected} domain.'
        f'</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# METRICS
# =========================================================

metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:

    st.metric(
        label="QUERIES TODAY",
        value="341",
        delta="12% from yesterday",
    )


with metric2:

    st.metric(
        label="GROUNDING RATE",
        value="96.4%",
        delta="High reliability",
    )


with metric3:

    st.metric(
        label="DOCUMENTS IN OCR",
        value="7",
        delta="Processing queue",
    )


with metric4:

    st.metric(
        label="STALE EMBEDDINGS",
        value="4",
        delta="Re-index recommended",
        delta_color="inverse",
    )


# =========================================================
# ASK NEXUS
# =========================================================

st.markdown(
    '<div class="ask-label">NEXUS INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ask-title">What do you need to understand?</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ask-description">'
    'Ask across your authorized company knowledge, systems and connected tools.'
    '</div>',
    unsafe_allow_html=True,
)


question = st.text_input(
    "Ask NEXUS",
    placeholder="Ask NEXUS anything...",
    label_visibility="collapsed",
)


# =========================================================
# QUICK ACCESS
# =========================================================

st.markdown(
    '<div class="section-title">Quick Access</div>',
    unsafe_allow_html=True,
)


quick1, quick2, quick3, quick4 = st.columns(4)


with quick1:

    st.markdown(
        '<div class="quick-card">'
        '<div class="quick-icon">⌘</div>'
        '<div class="quick-name">Engineering</div>'
        '<div class="quick-description">'
        'Code, architecture & systems'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with quick2:

    st.markdown(
        '<div class="quick-card">'
        '<div class="quick-icon">◇</div>'
        '<div class="quick-name">Product</div>'
        '<div class="quick-description">'
        'Roadmaps & requirements'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with quick3:

    st.markdown(
        '<div class="quick-card">'
        '<div class="quick-icon">◈</div>'
        '<div class="quick-name">Finance</div>'
        '<div class="quick-description">'
        'Budgets & financial knowledge'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with quick4:

    st.markdown(
        '<div class="quick-card">'
        '<div class="quick-icon">♙</div>'
        '<div class="quick-name">People</div>'
        '<div class="quick-description">'
        'Policies & employee knowledge'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# RECENT ACTIVITY
# =========================================================

st.markdown(
    '<div class="section-title">Recent Activity</div>',
    unsafe_allow_html=True,
)


activity_html = (
    '<div class="activity-card">'

    '<div class="activity-row">'
    '<div class="activity-name">'
    'Engineering architecture analysis'
    '</div>'
    '<div class="activity-meta">'
    'Engineering · Code Intelligence · 2m ago'
    '</div>'
    '</div>'

    '<div class="activity-row">'
    '<div class="activity-name">'
    'Q3 infrastructure budget question'
    '</div>'
    '<div class="activity-meta">'
    'Finance · Cross-domain · 14m ago'
    '</div>'
    '</div>'

    '<div class="activity-row">'
    '<div class="activity-name">'
    'Employee policy lookup'
    '</div>'
    '<div class="activity-meta">'
    'People / HR · 1h ago'
    '</div>'
    '</div>'

    '</div>'
)


st.markdown(
    activity_html,
    unsafe_allow_html=True,
)