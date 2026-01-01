import streamlit as st
from config import APP_TITLE
from components import inject_premium_css, top_navbar

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_premium_css()
top_navbar(active="Dashboard")


# =========================
# CSS SIMPLIFIÉ
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding: 2rem !important;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b4e 100%);
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: gridMove 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes gridMove {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .main > div {
        position: relative;
        z-index: 1;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    
    p, span, div, label {
        color: #cbd5e1 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 3rem !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 10px 40px rgba(124, 58, 237, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 20px 60px rgba(124, 58, 237, 0.7) !important;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.8) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 24px;
        padding: 2rem 1.5rem;
        transition: all 0.4s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.03);
        border-color: #a78bfa;
        box-shadow: 0 25px 80px rgba(124, 58, 237, 0.5);
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
</style>
""", unsafe_allow_html=True)


# =========================
# HERO
# =========================
st.markdown("<br><br><br>", unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
with col_b2:
    st.markdown("""
    <div style="text-align: center;">
        <span style="display: inline-block;
                     background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
                     color: white;
                     padding: 0.6rem 1.8rem;
                     border-radius: 50px;
                     font-size: 0.9rem;
                     font-weight: 800;
                     letter-spacing: 2px;
                     box-shadow: 0 8px 32px rgba(124, 58, 237, 0.6);">
            🚀 PLATEFORME #1 EN FRANCE
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<h1 style="text-align: center;
           font-size: 5rem;
           font-weight: 900;
           line-height: 1.1;
           margin: 1rem 0;
           background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 25%, #ec4899 50%, #f59e0b 75%, #10b981 100%);
           background-size: 200% 200%;
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           letter-spacing: -3px;">
    Votre Carrière Data & IA<br>Commence Ici
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="text-align: center;
          font-size: 1.8rem;
          color: #cbd5e1;
          font-weight: 300;
          max-width: 900px;
          margin: 1.5rem auto;
          line-height: 1.6;">
    Découvrez <span style="color: #60a5fa; font-weight: 600;">des milliers d'opportunités</span> dans l'IA, 
    la data science et le machine learning.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([1, 0.8, 0.4, 0.8, 1])
with col2:
    st.button("🎯 Explorer les Offres", use_container_width=True, key="btn1")
with col4:
    st.button("📊 Voir les Tendances", use_container_width=True, key="btn2")


# =========================
# STATS
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💼 Offres", "12,547")
with c2:
    st.metric("🏢 Entreprises", "2,340")
with c3:
    st.metric("🌍 Régions", "13")
with c4:
    st.metric("🚀 Satisfaction", "98%")


# =========================
# FEATURES
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<h2 style="text-align: center;
           font-size: 3rem;
           font-weight: 800;
           background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           margin-bottom: 3rem;">
    Pourquoi Nous Choisir ?
</h2>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("### 🤖 Matching IA")
    st.write("Algorithme ML qui analyse votre profil et recommande les offres pertinentes.")
with f2:
    st.markdown("### 📈 Insights Marché")
    st.write("Analyses sur les tendances salariales et compétences recherchées.")
with f3:
    st.markdown("### ⚡ Candidature Express")
    st.write("Postulez en un clic avec votre profil pré-rempli.")

st.markdown("<br>", unsafe_allow_html=True)

f4, f5, f6 = st.columns(3)
with f4:
    st.markdown("### 🎯 Alertes Perso")
    st.write("Notifications instantanées pour les offres qui vous correspondent.")
with f5:
    st.markdown("### 🔒 Confidentialité")
    st.write("Profil anonyme jusqu'à votre candidature.")
with f6:
    st.markdown("### 🌟 Entreprises Vérifiées")
    st.write("Partenaires vérifiés, leaders du secteur.")


# =========================
# TESTIMONIALS
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<h2 style="text-align: center;
           font-size: 3rem;
           font-weight: 800;
           background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           margin-bottom: 2rem;">
    Témoignages
</h2>
""", unsafe_allow_html=True)

# Testi 1
with st.container():
    st.info("*J'ai trouvé mon poste de Data Scientist en 2 semaines. Le matching IA est bluffant !*")
    tc1, tc2 = st.columns([0.1, 1])
    with tc1:
        st.markdown("🙋‍♀️")
    with tc2:
        st.markdown("**Marie D.** - Data Scientist @ Tech Corp")

st.markdown("<br>", unsafe_allow_html=True)

# Testi 2
with st.container():
    st.info("*Interface moderne. Les insights m'ont aidé à négocier un meilleur salaire !*")
    tc3, tc4 = st.columns([0.1, 1])
    with tc3:
        st.markdown("🙋‍♂️")
    with tc4:
        st.markdown("**Alexandre M.** - ML Engineer @ AI Startup")

st.markdown("<br>", unsafe_allow_html=True)

# Testi 3
with st.container():
    st.info("*La meilleure plateforme pour les métiers Data. Offres de qualité !*")
    tc5, tc6 = st.columns([0.1, 1])
    with tc5:
        st.markdown("🙋‍♀️")
    with tc6:
        st.markdown("**Sophie L.** - Data Analyst @ Finance Group")


# =========================
# FOOTER CTA
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.2) 0%, rgba(59, 130, 246, 0.15) 100%);
            border: 2px solid rgba(139, 92, 246, 0.4);
            border-radius: 30px;
            padding: 4rem 2rem;
            max-width: 1000px;
            margin: 0 auto;">
    <h2 style="font-size: 2.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 1rem;">
        Prêt à Booster Votre Carrière ?
    </h2>
    <p style="font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;">
        Rejoignez des milliers de professionnels qui ont trouvé leur opportunité idéale
    </p>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([1, 0.6, 1])
with col_f2:
    st.button("🚀 Commencer Maintenant", use_container_width=True, key="btn3")


# =========================
# FOOTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; 
            padding: 3rem 2rem; 
            border-top: 1px solid rgba(139, 92, 246, 0.2);">
    <p style="color: #94a3b8; font-size: 1rem; margin-bottom: 0.5rem;">
        <strong>DataJobs AI</strong> - La plateforme de référence pour les carrières Data & IA
    </p>
    <p style="color: #64748b; font-size: 0.9rem;">
        © 2025 DataJobs AI. Tous droits réservés.
    </p>
</div>
""", unsafe_allow_html=True)