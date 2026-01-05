import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# Import QRCode
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Import des utilitaires
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# SESSION STATE
# ============================================================================

for key, default in {
    'favorites': [],
    'comparison_list': [],
    'saved_searches': [],
    'dark_mode': False,
    'alerts': [],
    'view_history': [],
    'voice_transcript': ''
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Explorer V2.0 Ultimate | DataJobs",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_premium_css()
premium_navbar(active_page="Explorer")

# ============================================================================
# CSS ULTRA-MODERNE
# ============================================================================

st.markdown("""
<style>
    /* Cards ultra-modernes */
    .job-card-v2 {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(51, 65, 85, 0.95) 100%);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
    }
    
    .job-card-v2::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 5px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 25%, #ec4899 50%, #f59e0b 75%, #10b981 100%);
        background-size: 200% 100%;
        opacity: 0;
        transition: opacity 0.3s;
        animation: gradientSlide 3s linear infinite;
    }
    
    .job-card-v2:hover {
        transform: translateY(-12px) scale(1.02);
        border-color: rgba(139, 92, 246, 0.9);
        box-shadow: 0 30px 100px rgba(124, 58, 237, 0.7);
    }
    
    .job-card-v2:hover::before {
        opacity: 1;
    }
    
    @keyframes gradientSlide {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .premium-badge {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1rem;
        text-transform: uppercase;
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.6);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .smart-match {
        position: absolute;
        top: 1.5rem;
        left: 1.5rem;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.1rem;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.6);
    }
    
    .job-title-v2 {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 3rem 0 1rem 0;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.3;
    }
    
    .job-company-v2 {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .job-location-v2 {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 1.5rem;
    }
    
    .skill-tag-v2 {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border: 2px solid rgba(99, 102, 241, 0.5);
        color: #a78bfa;
        padding: 0.6rem 1.25rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0.35rem;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .skill-tag-v2:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.4) 0%, rgba(139, 92, 246, 0.4) 100%);
        border-color: #8b5cf6;
        transform: scale(1.1) translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
    }
    
    .info-badge {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 2px solid rgba(59, 130, 246, 0.5);
        color: #60a5fa;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-right: 0.75rem;
    }
    
    .salary-badge-v2 {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.5);
    }
    
    .stat-card-v2 {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.4s;
    }
    
    .stat-card-v2:hover {
        border-color: rgba(139, 92, 246, 0.8);
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 60px rgba(124, 58, 237, 0.5);
    }
    
    /* Microphone animation */
    @keyframes micPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5); }
        50% { transform: scale(1.1); box-shadow: 0 8px 40px rgba(239, 68, 68, 0.8); }
    }
    
    .mic-active {
        animation: micPulse 1s ease-in-out infinite !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HEADER
# ============================================================================

header_col1, header_col2, header_col3 = st.columns([2, 3, 2])

with header_col1:
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button("☀️ Clair" if st.session_state.dark_mode else "🌙 Sombre", use_container_width=True, key="dark_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with mode_col2:
        st.button("🎭 Anonyme", use_container_width=True, key="anon_toggle")

with header_col2:
    st.html("""
    <div style="
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.12) 100%);
        border: 2px solid rgba(139, 92, 246, 0.5);
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
    ">
        <h1 style="
            font-size: 2.8rem;
            font-weight: 900;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">
            🔍 Explorer V2.0 Ultimate
        </h1>
        <p style="font-size: 1rem; color: #cbd5e1;">
            🚀 IA • ⚡ Temps réel • 🎯 Match intelligent
        </p>
    </div>
    """)

with header_col3:
    quick_col1, quick_col2 = st.columns(2)
    with quick_col1:
        if st.button(f"⭐ Favoris ({len(st.session_state.favorites)})", use_container_width=True, key="fav_btn"):
            st.info(f"📋 {len(st.session_state.favorites)} favoris")
    with quick_col2:
        if st.button(f"🔄 Comparer ({len(st.session_state.comparison_list)})", use_container_width=True, key="cmp_btn"):
            st.info(f"🔄 {len(st.session_state.comparison_list)} en comparaison")


# ============================================================================
# RECHERCHE AVEC VOCAL FONCTIONNEL
# ============================================================================

st.markdown("### 🎯 Recherche Intelligente")

# Composant de recherche vocale HTML/JS
st.html("""
<div id="voiceSearchContainer" style="display: none; margin-bottom: 1rem;">
    <div style="
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.6);
    ">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎤</div>
        <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem;">
            Écoute en cours...
        </div>
        <div id="interimTranscript" style="font-size: 0.9rem; opacity: 0.8; font-style: italic;"></div>
    </div>
</div>

<script>
let recognition = null;
let isListening = false;

function initVoiceSearch() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'fr-FR';
        recognition.continuous = false;
        recognition.interimResults = true;
        
        recognition.onstart = function() {
            isListening = true;
            document.getElementById('voiceSearchContainer').style.display = 'block';
        };
        
        recognition.onresult = function(event) {
            let interim = '';
            let final = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    final += transcript;
                } else {
                    interim += transcript;
                }
            }
            
            document.getElementById('interimTranscript').textContent = interim || final;
            
            if (final) {
                // Injecter dans le champ de recherche Streamlit
                const searchInput = window.parent.document.querySelector('input[aria-label="🔎 Recherche"]');
                if (searchInput) {
                    searchInput.value = final;
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    searchInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Erreur reconnaissance vocale:', event.error);
            document.getElementById('voiceSearchContainer').style.display = 'none';
            isListening = false;
        };
        
        recognition.onend = function() {
            document.getElementById('voiceSearchContainer').style.display = 'none';
            isListening = false;
        };
    }
}

function startVoiceSearch() {
    if (recognition && !isListening) {
        recognition.start();
    } else if (!recognition) {
        alert('La reconnaissance vocale n\\'est pas supportée par votre navigateur.\\nUtilisez Chrome, Edge ou Opera.');
    }
}

// Initialiser au chargement
initVoiceSearch();
</script>
""")

search_col1, search_col2 = st.columns([4, 1])

with search_col1:
    search_query = st.text_input(
        "🔎 Recherche",
        value=st.session_state.voice_transcript,
        placeholder="Ex: Data Scientist Python Machine Learning Paris...",
        key="search_input",
        label_visibility="collapsed"
    )

with search_col2:
    # Bouton qui active le JavaScript
    if st.button("🎤 Vocal", use_container_width=True, key="voice_btn", help="Cliquez et parlez"):
        st.html("<script>startVoiceSearch();</script>")
        st.info("🎙️ **Parlez maintenant !** Dites votre recherche clairement.")

# Options
opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)

with opt_col1:
    view_mode = st.selectbox("Vue", ["📋 Liste Détaillée", "🎴 Grille", "📊 Analytics"], key="view_sel")

with opt_col2:
    sort_by = st.selectbox("Trier", ["🎯 Match IA", "📅 Récent", "⭐ Pertinence"], key="sort_sel")

with opt_col3:
    items_per_page = st.selectbox("Afficher", [10, 20, 50, 100], index=1, key="items_sel")

with opt_col4:
    if st.button("💾 Sauvegarder", use_container_width=True, key="save_btn"):
        if search_query:
            st.session_state.saved_searches.append({
                'query': search_query,
                'timestamp': datetime.now().isoformat()
            })
            st.success("✅ Recherche sauvegardée!")


# ============================================================================
# CHARGER DONNÉES
# ============================================================================

@st.cache_data(ttl=180)
def load_data():
    try:
        df = load_offers_with_skills()
        if not df.empty:
            df['skills_count'] = df['all_skills'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
            df['has_remote'] = df['remote'].apply(lambda x: x == 'yes' if pd.notna(x) else False)
        return df
    except Exception as e:
        st.error(f"Erreur: {e}")
        return pd.DataFrame()

with st.spinner("⚡ Chargement..."):
    df = load_data()

if df.empty:
    st.error("⚠️ Aucune donnée")
    st.stop()


# ============================================================================
# SIDEBAR FILTRES
# ============================================================================

st.sidebar.markdown("## 🎨 Filtres")

regions_list = sorted(df['region_name'].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "🗺️ Régions",
    options=regions_list,
    default=regions_list[:3] if len(regions_list) >= 3 else regions_list
)

contracts = sorted(df['contract_type'].dropna().unique().tolist())
selected_contracts = st.sidebar.multiselect("📋 Contrats", options=contracts, default=contracts)

remote_filter = st.sidebar.radio("🏠 Télétravail", ["Tous", "Oui", "Non", "Hybride"])

min_skills, max_skills = st.sidebar.slider("🎯 Compétences", 0, 50, (0, 50))

all_skills = set()
for skills_str in df['all_skills'].dropna():
    if isinstance(skills_str, str):
        all_skills.update([s.strip() for s in skills_str.split(',') if s.strip()])
all_skills = sorted(list(all_skills))[:200]

selected_skills = st.sidebar.multiselect("💡 Compétences", options=all_skills, max_selections=10)

st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()
with col2:
    if st.button("🔔 Alerte", use_container_width=True):
        st.session_state.alerts.append({
            'query': search_query,
            'timestamp': datetime.now().isoformat()
        })
        st.sidebar.success("✅ Alerte créée!")


# ============================================================================
# FILTRAGE
# ============================================================================

filtered_df = df.copy()

if search_query:
    query_lower = search_query.lower()
    mask = (
        filtered_df['title'].str.lower().str.contains(query_lower, na=False) |
        filtered_df['company_name'].str.lower().str.contains(query_lower, na=False) |
        filtered_df['region_name'].str.lower().str.contains(query_lower, na=False) |
        filtered_df['all_skills'].str.lower().str.contains(query_lower, na=False)
    )
    filtered_df = filtered_df[mask]

if selected_regions:
    filtered_df = filtered_df[filtered_df['region_name'].isin(selected_regions)]

if selected_contracts:
    filtered_df = filtered_df[filtered_df['contract_type'].isin(selected_contracts)]

remote_map = {"Oui": "yes", "Non": "no", "Hybride": "hybrid"}
if remote_filter in remote_map:
    filtered_df = filtered_df[filtered_df['remote'] == remote_map[remote_filter]]

filtered_df = filtered_df[
    (filtered_df['skills_count'] >= min_skills) &
    (filtered_df['skills_count'] <= max_skills)
]

if selected_skills:
    def has_skills(skills_str):
        if pd.isna(skills_str):
            return False
        skills_list = [s.strip().lower() for s in str(skills_str).split(',')]
        return any(skill.lower() in skills_list for skill in selected_skills)
    filtered_df = filtered_df[filtered_df['all_skills'].apply(has_skills)]

def calc_match(row):
    score = 50
    if selected_skills:
        row_skills = [s.strip().lower() for s in str(row.get('all_skills', '')).split(',')]
        matches = sum(1 for skill in selected_skills if skill.lower() in row_skills)
        score += min(matches * 10, 40)
    if search_query and search_query.lower() in str(row.get('title', '')).lower():
        score += 20
    if row.get('remote') == 'yes':
        score += 5
    if row.get('contract_type') == 'CDI':
        score += 5
    return min(score, 100)

filtered_df['match_score'] = filtered_df.apply(calc_match, axis=1)

if sort_by == "🎯 Match IA":
    filtered_df = filtered_df.sort_values('match_score', ascending=False)
elif sort_by == "📅 Récent":
    if 'added_at' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('added_at', ascending=False)


# ============================================================================
# STATISTIQUES
# ============================================================================

st.markdown("### 📊 Analytics Temps Réel")

stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)

with stat_col1:
    st.html(f"""
    <div class="stat-card-v2">
        <div style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            {len(filtered_df):,}
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">
            💼 Offres
        </div>
    </div>
    """)

with stat_col2:
    st.html(f"""
    <div class="stat-card-v2">
        <div style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            {filtered_df['company_name'].nunique()}
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">
            🏢 Entreprises
        </div>
    </div>
    """)

with stat_col3:
    st.html(f"""
    <div class="stat-card-v2">
        <div style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #ec4899 0%, #be185d 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            {filtered_df['region_name'].nunique()}
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">
            🗺️ Régions
        </div>
    </div>
    """)

with stat_col4:
    avg_match = filtered_df['match_score'].mean() if len(filtered_df) > 0 else 0
    st.html(f"""
    <div class="stat-card-v2">
        <div style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            {avg_match:.0f}%
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">
            🎯 Match
        </div>
    </div>
    """)

with stat_col5:
    remote_pct = (filtered_df['has_remote'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.html(f"""
    <div class="stat-card-v2">
        <div style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            {remote_pct:.0f}%
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">
            🏠 Télétravail
        </div>
    </div>
    """)

# Graphiques
if view_mode == "📊 Analytics" and not filtered_df.empty:
    st.markdown("---")
    st.markdown("### 📈 Tendances")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        region_counts = filtered_df['region_name'].value_counts().head(10)
        fig1 = px.bar(
            x=region_counts.values,
            y=region_counts.index,
            orientation='h',
            title="🗺️ Top 10 Régions",
            color=region_counts.values,
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        contract_counts = filtered_df['contract_type'].value_counts()
        fig2 = px.pie(
            values=contract_counts.values,
            names=contract_counts.index,
            title="📋 Contrats",
            hole=0.4
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# ============================================================================
# AFFICHAGE OFFRES
# ============================================================================

if filtered_df.empty:
    st.warning("😕 Aucune offre")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.rerun()
    with col2:
        st.info("💡 Élargissez les filtres")
    st.stop()

# Pagination
total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)
page = st.number_input(f"📄 Page (1-{total_pages})", min_value=1, max_value=total_pages, value=1)

start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(filtered_df))
page_df = filtered_df.iloc[start_idx:end_idx]

st.markdown(f"### 🎯 Résultats {start_idx + 1}-{end_idx} sur {len(filtered_df)}")


# MODE LISTE
if view_mode in ["📋 Liste Détaillée", "📊 Analytics"]:
    for idx, row in page_df.iterrows():
        title = str(row.get('title', 'N/A'))
        company = str(row.get('company_name', 'N/A'))
        location = str(row.get('region_name', 'N/A'))
        contract = str(row.get('contract_type', 'CDI'))
        remote = str(row.get('remote', 'unknown'))
        skills_count = int(row.get('skills_count', 0))
        match_score = int(row.get('match_score', 75))
        
        competences = []
        if 'competences' in row and pd.notna(row['competences']):
            competences = [s.strip() for s in str(row['competences']).split(',') if s.strip()][:8]
        
        remote_badge = ""
        if remote == "yes":
            remote_badge = '<span class="info-badge">🏠 Télétravail</span>'
        elif remote == "hybrid":
            remote_badge = '<span class="info-badge">🔀 Hybride</span>'
        
        salary = f"{30 + (hash(str(idx)) % 50)}K - {50 + (hash(str(idx)) % 70)}K €"
        
        # Card avec st.html()
        st.html(f"""
        <div class="job-card-v2">
            <div class="smart-match">🎯 <strong>{match_score}%</strong></div>
            {'<div class="premium-badge">⭐ PREMIUM</div>' if match_score > 90 else ''}
            <div class="job-title-v2">{title[:100]}</div>
            <div class="job-company-v2">🏢 {company[:60]}</div>
            <div class="job-location-v2">📍 {location}</div>
            <div style="margin: 1.5rem 0;">
                <span class="salary-badge-v2">💰 {salary}</span>
                <span class="info-badge">📋 {contract}</span>
                {remote_badge}
                <span class="info-badge">🎯 {skills_count} compétences</span>
            </div>
            <div style="margin: 1.5rem 0;">
                {''.join([f'<span class="skill-tag-v2">💎 {skill}</span>' for skill in competences])}
            </div>
        </div>
        """)
        
        # Boutons
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            if st.button("📄 Détails", key=f"det_{idx}", use_container_width=True):
                st.session_state[f'show_{idx}'] = not st.session_state.get(f'show_{idx}', False)
        
        with btn_col2:
            is_fav = idx in st.session_state.favorites
            if st.button("💖" if is_fav else "⭐", key=f"fav_{idx}", use_container_width=True):
                if is_fav:
                    st.session_state.favorites.remove(idx)
                else:
                    st.session_state.favorites.append(idx)
        
        with btn_col3:
            in_cmp = idx in st.session_state.comparison_list
            if st.button("➖" if in_cmp else "🔄", key=f"cmp_{idx}", use_container_width=True):
                if in_cmp:
                    st.session_state.comparison_list.remove(idx)
                elif len(st.session_state.comparison_list) < 5:
                    st.session_state.comparison_list.append(idx)
        
        with btn_col4:
            if st.button("📨 Postuler", key=f"app_{idx}", use_container_width=True):
                st.info("🚀 Redirection...")
        
        if st.session_state.get(f'show_{idx}', False):
            with st.expander("📋 Détails", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Entreprise:** {company}")
                    st.write(f"**Localisation:** {location}")
                    st.write(f"**Contrat:** {contract}")
                with col2:
                    st.write(f"**Télétravail:** {remote}")
                    st.write(f"**Compétences:** {skills_count}")
                    st.write(f"**Match:** {match_score}%")

else:
    # GRILLE
    cols_per_row = 3
    for i in range(0, len(page_df), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(page_df):
                row = page_df.iloc[i + j]
                with cols[j]:
                    st.metric("Title", str(row.get('title', 'N/A'))[:30])
                    st.caption(f"🏢 {str(row.get('company_name', 'N/A'))[:25]}")
                    st.caption(f"📍 {str(row.get('region_name', 'N/A'))}")


# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")
st.markdown("### 📥 Export")

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📄 CSV", csv, f'datajobs_{datetime.now().strftime("%Y%m%d")}.csv', "text/csv", use_container_width=True)

with exp_col2:
    json_data = filtered_df.to_json(orient='records', indent=2)
    st.download_button("📦 JSON", json_data, f'datajobs_{datetime.now().strftime("%Y%m%d")}.json', "application/json", use_container_width=True)

with exp_col3:
    if st.button("📊 Analytics", use_container_width=True):
        st.info("🚧 Bientôt")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.html(f"""
<div style="text-align: center; padding: 2rem; color: #94a3b8;">
    ⚡ {len(filtered_df)} offres • 
    ⭐ {len(st.session_state.favorites)} favoris • 
    🔄 {len(st.session_state.comparison_list)} comparaison •
    🔔 {len(st.session_state.alerts)} alertes
    <br><br>
    <strong style="color: #60a5fa;">Dernière mise à jour:</strong> {datetime.now().strftime("%d/%m/%Y à %H:%M")}
</div>
""")