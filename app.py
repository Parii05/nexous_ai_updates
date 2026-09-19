"""NEXUS command center.

The domain agents are implemented as Streamlit multipage routes under pages/.
The shared visual system and API interactions live in Components.py.
"""
import streamlit as st

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

configure_page("Command Center")
init_session_state()
inject_css()

render_sidebar("All Domains")
render_header("All Domains")
render_metrics()
render_ask_and_result("All Domains")
render_quick_access()
render_recent_activity()
