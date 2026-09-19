import streamlit as st
from Components import configure_page, init_session_state, render_domain_workspace

configure_page("Product")
init_session_state()
render_domain_workspace("Product")
