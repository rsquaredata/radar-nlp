from __future__ import annotations

import streamlit as st


def inject_premium_css() -> None:
    """Injecte le CSS global amélioré mais robuste."""
    st.markdown(
        """
<style>
/* =================================================================== */
/* 1) MASQUER LA SIDEBAR STREAMLIT                                     */
/* =================================================================== */

[data-testid="stSidebar"], [data-testid="stSidebarNav"] {
    display: none !important;
}

[data-testid="stAppViewContainer"] > .main {
    margin-left: 0 !important;
}

/* FULL WIDTH LAYOUT */
main .block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* =================================================================== */
/* 2) BACKGROUND GLOBAL AMÉLIORÉ                                       */
/* =================================================================== */

.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b4e 100%);
    color: #e5e7eb;
}

/* Grille subtile en arrière-plan */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

h1, h2, h3, h4, h5 {
    color: #f9fafb !important;
    letter-spacing: .04em;
}

.stMarkdown, p, label, span, .stCaption, .stText {
    color: #e5e7eb;
}

/* =================================================================== */
/* 3) NAVBAR MODERNE ET ROBUSTE                                        */
/* =================================================================== */

.top-nav-wrapper {
    margin-bottom: 1.5rem;
    width: 100% !important;
}

.app-pill {
    width: 100% !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    border-radius: 20px;
    border: 2px solid rgba(139, 92, 246, 0.4);
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.95) 0%, 
        rgba(51, 65, 85, 0.9) 100%);
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.5),
        0 0 60px rgba(124, 58, 237, 0.3);
    position: relative;
    overflow: hidden;
}

/* Barre de couleur en haut */
.app-pill::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, 
        #7c3aed 0%, 
        #3b82f6 33%, 
        #10b981 66%, 
        #ec4899 100%);
}

.app-pill-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.app-pill-icon {
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.5);
    transition: all 0.3s ease;
}

.app-pill-icon:hover {
    transform: scale(1.1) rotate(5deg);
}

.app-pill-title {
    font-weight: 800;
    font-size: 1.1rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.app-pill-sub {
    font-size: 0.85rem;
    opacity: .9;
    color: #94a3b8;
    margin-top: 0.25rem;
}

.live-badge {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5);
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { 
        transform: scale(1); 
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5);
    }
    50% { 
        transform: scale(1.05); 
        box-shadow: 0 6px 30px rgba(239, 68, 68, 0.7);
    }
}

/* Boutons de navigation */
.top-nav-row {
    margin-top: 1rem;
    display: flex;
    gap: 0.75rem;
    width: 100% !important;
    flex-wrap: wrap;
}

.top-nav-row [data-testid="stPageLink"] {
    flex: 1;
    min-width: 140px;
}

.top-nav-row [data-testid="stPageLink"] > div {
    height: 50px;
    border-radius: 14px;
    border: 2px solid rgba(148, 163, 184, 0.3);
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.8) 0%, 
        rgba(51, 65, 85, 0.6) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #cbd5e1;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.top-nav-row [data-testid="stPageLink"] > div:hover {
    transform: translateY(-3px);
    border-color: rgba(139, 92, 246, 0.6);
    box-shadow: 
        0 10px 40px rgba(124, 58, 237, 0.4),
        0 0 60px rgba(59, 130, 246, 0.2);
    color: #f8fafc;
    background: linear-gradient(135deg, 
        rgba(124, 58, 237, 0.3) 0%, 
        rgba(59, 130, 246, 0.2) 100%);
}

/* Page active */
.top-nav-row [data-testid="stPageLink"][aria-current="page"] > div {
    background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
    border-color: rgba(139, 92, 246, 0.8);
    color: white;
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.5);
}

/* =================================================================== */
/* 4) SELECTBOX AMÉLIORÉ                                              */
/* =================================================================== */

.stSelectbox label {
    color: #f9fafb !important;
    font-size: 0.95rem;
    font-weight: 600;
}

.stSelectbox > div > div {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 2px solid rgba(148, 163, 184, 0.3) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
}

.stSelectbox > div > div:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
}

[data-baseweb="select"] * {
    color: #f8fafc !important;
}

[data-baseweb="select"] [role="listbox"] {
    background-color: rgba(30, 41, 59, 0.95) !important;
    border: 2px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
}

[data-baseweb="select"] [role="option"][aria-selected="true"] {
    background-color: rgba(124, 58, 237, 0.3) !important;
}

[data-baseweb="select"] [role="option"]:hover {
    background-color: rgba(139, 92, 246, 0.2) !important;
}

/* =================================================================== */
/* 5) METRICS PREMIUM                                                  */
/* =================================================================== */

.stMetric {
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.95) 0%, 
        rgba(51, 65, 85, 0.8) 100%);
    border-radius: 18px;
    padding: 1.5rem;
    border: 2px solid rgba(139, 92, 246, 0.3);
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
}

.stMetric:hover {
    transform: translateY(-4px);
    border-color: rgba(139, 92, 246, 0.6);
    box-shadow: 
        0 12px 48px rgba(124, 58, 237, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.stMetric label {
    color: #94a3b8 !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.85rem;
}

.stMetric [data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 900;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* =================================================================== */
/* 6) RESPONSIVE                                                       */
/* =================================================================== */

@media (max-width: 768px) {
    .app-pill {
        flex-direction: column;
        text-align: center;
    }
    
    .top-nav-row {
        flex-direction: column;
    }
    
    .top-nav-row [data-testid="stPageLink"] {
        width: 100%;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def top_navbar(active: str = "Dashboard") -> None:
    """
    Navbar moderne et robuste - Version testée et fonctionnelle.
    """

    # Header de la navbar
    st.markdown(
        """
<div class="top-nav-wrapper">
  <div class="app-pill">
    <div class="app-pill-left">
      <div class="app-pill-icon">🧠</div>
      <div>
        <div class="app-pill-title">JOBscope — Data &amp; IA</div>
        <div class="app-pill-sub">France Travail • HelloWork • Adzuna</div>
      </div>
    </div>
    <div class="live-badge">🔴 LIVE</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Boutons de navigation
    nav_items = [
        ("Dashboard", "📊", "pages/dashboard.py"),
        ("Carte", "🗺️", "pages/cartes.py"),
        ("Offres", "📋", "pages/offres.py"),
        ("Clusters", "🧠", "pages/clusters.py"),
        ("Ajouter", "➕", "pages/ajouter_une_offre.py"),
    ]

    st.markdown('<div class="top-nav-row">', unsafe_allow_html=True)
    cols = st.columns(len(nav_items))
    for col, (label, icon, page_path) in zip(cols, nav_items):
        with col:
            st.page_link(page_path, label=f"{icon} {label}")
    st.markdown('</div>', unsafe_allow_html=True)