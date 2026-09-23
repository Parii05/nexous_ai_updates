"""NEXUS command center.

The domain agents are implemented as Streamlit multipage routes under pages/.
The shared visual system and API interactions live in Components.py.
"""
import streamlit as st

from auth import sign_in, sign_up
from Components import (
    configure_page,
    init_session_state,
    inject_css,
    render_sidebar,
    render_header,
    render_metrics,
    render_ask_and_result,
    render_quick_access,
    render_recent_activity,
)


def _require_auth():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""

    if not st.session_state.logged_in:
        st.set_page_config(page_title="NEXUS Login", page_icon="🔐", layout="centered")
        st.title("NEXUS Login")

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    try:
                        user = sign_in(email, password)
                        st.session_state.logged_in = True
                        st.session_state.user_email = user["email"]
                        st.success("Login successful")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        with tab_signup:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                submit = st.form_submit_button("Create Account")

                if submit:
                    try:
                        user = sign_up(email, password)
                        st.session_state.logged_in = True
                        st.session_state.user_email = user["email"]
                        st.success("Account created successfully")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        st.stop()


_require_auth()
configure_page("Command Center")
init_session_state()
inject_css()

st.sidebar.title("NEXUS")
st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.rerun()

render_sidebar("All Domains")
render_header("All Domains")
render_metrics()
render_ask_and_result("All Domains")
render_quick_access()
render_recent_activity()
