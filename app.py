
import streamlit as st

st.set_page_config(
    page_title="SCC Dashboard",
    page_icon="🌍",
    layout="wide"
)

pg = st.navigation(
    [
        st.Page(
            "index.py",
            title="Home",
            icon="🏠",
            default=True
        ),
        st.Page(
            "main.py",
            title="Dashboard",
            icon="📊"
        )
    ],
    position="hidden"
)

pg.run()
