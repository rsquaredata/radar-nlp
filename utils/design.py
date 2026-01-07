import streamlit as st

def inject_premium_style():
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); color: #FAFAFA; }
        .main-title { 
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 3rem; font-weight: 800; text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
