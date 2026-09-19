import streamlit as st
from Components import configure_page, init_session_state, render_domain_workspace

configure_page("People / HR")
init_session_state()
render_domain_workspace("People / HR")
