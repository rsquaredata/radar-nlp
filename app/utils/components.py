import streamlit as st
from typing import Optional, List, Dict, Any



def inject_premium_css():
    """Injecte le CSS global moderne et professionnel"""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body, [data-testid="stAppViewContainer"], .main {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b4e 100%);
            color: #f8fafc;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(236, 72, 153, 0.12) 0%, transparent 50%),
                linear-gradient(rgba(99, 102, 241, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(99, 102, 241, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
            animation: backgroundPulse 15s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        @keyframes backgroundPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        .main .block-container {
            max-width: 1400px !important;
            padding: 2rem 3rem !important;
            position: relative;
            z-index: 1;
        }
        
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            color: #f8fafc !important;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        h1 {
            font-size: 4rem;
            font-weight: 900;
            line-height: 1.1;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 8s ease infinite;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        h2 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        h3 {
            font-size: 1.75rem;
            color: #f8fafc !important;
        }
        
        p, span, div, label {
            color: #cbd5e1 !important;
            line-height: 1.7;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 2.5rem !important;
            border-radius: 32px !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 20px 60px rgba(124, 58, 237, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 25px 80px rgba(124, 58, 237, 0.6) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) scale(0.98) !important;
        }
        
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
            border: 2px solid rgba(139, 92, 246, 0.3);
            border-radius: 24px;
            padding: 2rem 1.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        [data-testid="metric-container"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: rgba(139, 92, 246, 0.6);
            box-shadow: 0 20px 60px rgba(124, 58, 237, 0.4);
        }
        
        [data-testid="metric-container"]:hover::before {
            opacity: 1;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 3rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 2px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 18px !important;
            color: #f8fafc !important;
            padding: 0.875rem 1.25rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            background: rgba(30, 41, 59, 0.95) !important;
        }
        
        .stTextInput > label,
        .stSelectbox > label {
            color: #f8fafc !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .stPageLink {
            width: 100%;
        }
        
        .stPageLink > a {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.875rem 1.5rem;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.7) 100%);
            border: 2px solid rgba(148, 163, 184, 0.3);
            border-radius: 14px;
            color: #cbd5e1;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .stPageLink > a:hover {
            transform: translateY(-3px);
            border-color: rgba(139, 92, 246, 0.6);
            box-shadow: 0 10px 40px rgba(124, 58, 237, 0.4);
            color: #f8fafc;
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.3) 0%, rgba(59, 130, 246, 0.2) 100%);
        }
        
        .stPageLink[aria-current="page"] > a {
            background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
            border-color: rgba(139, 92, 246, 0.8);
            color: white;
            box-shadow: 0 8px 32px rgba(124, 58, 237, 0.5);
        }
        
        [data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        .streamlit-expanderHeader {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 2px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 18px !important;
            color: #f8fafc !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: rgba(139, 92, 246, 0.6) !important;
            background: rgba(30, 41, 59, 0.95) !important;
        }
        
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 10px;
            border: 2px solid rgba(30, 41, 59, 0.5);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.8; }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        @keyframes gradientSlide {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }
        
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem !important;
            }
            h1 { font-size: 2.5rem; }
            h2 { font-size: 1.75rem; }
            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                font-size: 2rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# NAVBAR RÉVOLUTIONNAIRE AVEC LIENS ACTIFS
# ============================================================================

def premium_navbar(active_page: str = "Home"):
    
    
    # Container principal
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(51, 65, 85, 0.95) 100%);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(139, 92, 246, 0.3);
            border-radius: 32px;
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), 0 0 60px rgba(99, 102, 241, 0.3);
            position: relative;
            overflow: hidden;
        '>
            <div style='
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 25%, #ec4899 50%, #f59e0b 75%, #10b981 100%);
                background-size: 200% 100%;
                animation: gradientSlide 3s linear infinite;
            '></div>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='display: flex; align-items: center; gap: 1.25rem;'>
                    <div style='
                        width: 56px; height: 56px;
                        border-radius: 16px;
                        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 1.75rem;
                        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.5);
                    '>🧠</div>
                    <div>
                        <div style='
                            font-family: "Space Grotesk", sans-serif;
                            font-size: 1.5rem;
                            font-weight: 800;
                            letter-spacing: -0.02em;
                            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        '>RadarJobs Analytics</div>
                        <div style='font-size: 0.85rem; color: #94a3b8; font-weight: 500; margin-top: 0.15rem;'>
                            France Travail • HelloWork 
                        </div>
                    </div>
                </div>
                <div style='
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                    color: white;
                    padding: 0.65rem 1.25rem;
                    border-radius: 50px;
                    font-size: 0.8rem;
                    font-weight: 800;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                    box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5);
                    animation: pulse 2s ease-in-out infinite;
                    display: flex; align-items: center; gap: 0.5rem;
                '>
                    <span style='width: 8px; height: 8px; background: white; border-radius: 50%; animation: pulse 1s ease-in-out infinite;'></span>
                    LIVE
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation avec liens ACTIFS
    pages = [
        ("Home", "🏠", "home.py"),
        ("Explorer", "🔍", "pages/Explorer.py"),
        ("Analytics", "📊", "pages/Analytics.py"),
        ("Intelligence", "🧠", "pages/Intelligence.py"),
        ("Géographie", "🗺️", "pages/Geographie.py"),
        ("Contribuer", "➕", "pages/Contribuer.py"),
        ("Assistant", "🤖", "pages/Assistant.py"),
    ]
    
    cols = st.columns(len(pages))
    
    for col, (label, icon, page_path) in zip(cols, pages):
        with col:
            if active_page == label:
                st.markdown(f"""
                <div style='
                    padding: 0.875rem 1.5rem;
                    background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
                    border: 2px solid rgba(139, 92, 246, 0.8);
                    border-radius: 14px;
                    color: white;
                    font-size: 0.95rem;
                    font-weight: 600;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.5);
                '>
                    {icon} {label}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.page_link(
                    page_path,
                    label=f"{icon} {label}",
                    use_container_width=True
                )
