import streamlit as st
from Components import configure_page, init_session_state, render_domain_workspace

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()

configure_page("Finance")
init_session_state()
render_domain_workspace("Finance")
