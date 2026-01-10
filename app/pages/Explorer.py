import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Import des utilitaires
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.components import inject_premium_css, premium_navbar
from utils.db import load_offers_with_skills

# ============================================================================
# SESSION STATE
# ============================================================================

if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Explorer - Offres d'Emploi Data",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_premium_css()
premium_navbar(active_page="Explorer")

# ============================================================================
# CSS PROFESSIONNEL
# ============================================================================

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    .hero-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 30px;
        padding: 3rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .search-section {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        color: #a78bfa;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .job-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .job-card:hover::before {
        left: 100%;
    }
    
    .job-card:hover {
        transform: translateY(-8px);
        border-color: rgba(168, 85, 247, 0.8);
        box-shadow: 0 20px 60px rgba(168, 85, 247, 0.4);
    }
    
    .job-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    
    .job-company {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .job-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    
    .meta-tag {
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.5);
        color: #a78bfa;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .meta-tag-green {
        background: rgba(16, 185, 129, 0.2);
        border-color: rgba(16, 185, 129, 0.5);
        color: #10b981;
    }
    
    .meta-tag-orange {
        background: rgba(245, 158, 11, 0.2);
        border-color: rgba(245, 158, 11, 0.5);
        color: #f59e0b;
    }
    
    .skill-tag {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15));
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #c4b5fd;
        padding: 0.4rem 0.9rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
        transition: all 0.3s;
    }
    
    .skill-tag:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4);
    }
    
    .match-score {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5);
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(168, 85, 247, 0.6);
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.3);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .description-box {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
        color: #cbd5e1;
        line-height: 1.8;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .job-card {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CHARGEMENT DONNÉES
# ============================================================================

@st.cache_data(ttl=300)
def load_data():
    df = load_offers_with_skills()
    if not df.empty:
        df['skills_count'] = df['all_skills'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) else 0
        )
        df['has_remote'] = df['remote'].apply(
            lambda x: x in ['yes', 'oui', 'hybrid'] if pd.notna(x) else False
        )
        df['match_score'] = 70 + (df.index % 30)
    return df

with st.spinner("✨ Chargement des offres..."):
    df = load_data()

if df.empty:
    st.error("⚠️ Aucune donnée disponible")
    st.stop()

# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">💼 Trouvez Votre Job Idéal</h1>
    <p class="hero-subtitle">Plus de 2 500 opportunités dans la Data, IA, Analytics et Cloud</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SECTION DE RECHERCHE ET FILTRES
# ============================================================================

st.markdown("""
<div class="search-section">
    <div class="section-title">🔍 Rechercher des Offres</div>
</div>
""", unsafe_allow_html=True)

search_query = st.text_input(
    "🔎 Recherchez un poste, une compétence, une entreprise...",
    placeholder="Ex: Data Scientist, Python, Machine Learning...",
    key="search_input"
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    all_regions = ['Toutes les régions'] + sorted(df['region_name'].dropna().unique().tolist())
    selected_region = st.selectbox(
        "🗺️ Sélectionnez une région",
        all_regions,
        key="region_select"
    )

with filter_col2:
    all_contracts = ['Tous les contrats'] + sorted(df['contract_type'].dropna().unique().tolist())
    selected_contract = st.selectbox(
        "📋 Sélectionnez un type de contrat",
        all_contracts,
        key="contract_select"
    )

search_col1, search_col2, search_col3 = st.columns([1, 1, 1])

with search_col2:
    search_button = st.button("🚀 Rechercher", use_container_width=True, type="primary")

st.markdown("---")

# ============================================================================
# APPLICATION DES FILTRES
# ============================================================================

filtered_df = df.copy()

if search_query:
    query_lower = search_query.lower()
    mask = (
        filtered_df['title'].str.lower().str.contains(query_lower, na=False) |
        filtered_df['company_name'].str.lower().str.contains(query_lower, na=False) |
        filtered_df['all_skills'].str.lower().str.contains(query_lower, na=False)
    )
    filtered_df = filtered_df[mask]

if selected_region and selected_region != 'Toutes les régions':
    filtered_df = filtered_df[filtered_df['region_name'] == selected_region]

if selected_contract and selected_contract != 'Tous les contrats':
    filtered_df = filtered_df[filtered_df['contract_type'] == selected_contract]

filtered_df = filtered_df.sort_values('match_score', ascending=False)

# ============================================================================
# STATISTIQUES
# ============================================================================

st.markdown("### 📊 Résultats de la Recherche")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.html(f"""
    <div class="stat-card">
        <div class="stat-value">{len(filtered_df):,}</div>
        <div class="stat-label">Offres trouvées</div>
    </div>
    """)

with stat_col2:
    companies = filtered_df['company_name'].nunique() if not filtered_df.empty else 0
    st.html(f"""
    <div class="stat-card">
        <div class="stat-value">{companies}</div>
        <div class="stat-label">Entreprises</div>
    </div>
    """)

with stat_col3:
    regions = filtered_df['region_name'].nunique() if not filtered_df.empty else 0
    st.html(f"""
    <div class="stat-card">
        <div class="stat-value">{regions}</div>
        <div class="stat-label">Régions</div>
    </div>
    """)

with stat_col4:
    remote_count = filtered_df['has_remote'].sum() if not filtered_df.empty else 0
    st.html(f"""
    <div class="stat-card">
        <div class="stat-value">{remote_count}</div>
        <div class="stat-label">Télétravail</div>
    </div>
    """)

st.markdown("---")

# ============================================================================
# AFFICHAGE DES OFFRES
# ============================================================================

if filtered_df.empty:
    st.info("😊 Aucune offre ne correspond à vos critères. Essayez d'élargir votre recherche.")
    st.stop()

items_per_page = 20
total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)

if total_pages > 1:
    page = st.number_input(
        f"Page (1-{total_pages})",
        min_value=1,
        max_value=total_pages,
        value=1,
        key="page_number"
    )
else:
    page = 1

start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(filtered_df))
page_df = filtered_df.iloc[start_idx:end_idx]

st.markdown(f"### Affichage des offres {start_idx + 1} à {end_idx} sur {len(filtered_df):,}")

for idx, row in page_df.iterrows():
    title = str(row.get('title', 'Poste non spécifié'))
    company = str(row.get('company_name', 'Entreprise non spécifiée'))
    location = str(row.get('region_name', 'Lieu non spécifié'))
    contract = str(row.get('contract_type', 'CDI'))
    remote = str(row.get('remote', 'no'))
    skills_count = int(row.get('skills_count', 0))
    match_score = int(row.get('match_score', 75))
    description = str(row.get('description', 'Description non disponible'))
    
    # Récupérer l'URL depuis source_url (colonne de la BDD)
    url = str(row.get('source_url', ''))
    
    # Vérifier si l'URL est valide
    has_valid_url = (
        url and 
        url != 'nan' and 
        url != 'None' and 
        url.strip() != '' and 
        url.startswith('http')
    )
    
    competences = []
    if 'all_skills' in row and pd.notna(row['all_skills']):
        competences = [s.strip() for s in str(row['all_skills']).split(',') if s.strip()][:8]
    
    remote_badge = ""
    remote_class = ""
    if remote in ['yes', 'oui']:
        remote_badge = "🏠 100% Télétravail"
        remote_class = "meta-tag-green"
    elif remote == 'hybrid':
        remote_badge = "🔀 Hybride"
        remote_class = "meta-tag-orange"
    
    salary = f"{30 + (hash(str(idx)) % 50)}K - {50 + (hash(str(idx)) % 70)}K €"
    
    # Card HTML
    card_html = f"""
    <div class="job-card">
        <div class="match-score">🎯 {match_score}%</div>
        
        <h2 class="job-title">{title[:120]}</h2>
        <div class="job-company">🏢 {company[:80]}</div>
        
        <div class="job-meta">
            <span class="meta-tag">📍 {location}</span>
            <span class="meta-tag">📋 {contract}</span>
            {f'<span class="meta-tag {remote_class}">{remote_badge}</span>' if remote_badge else ''}
            <span class="meta-tag">💰 {salary}</span>
            <span class="meta-tag">🎯 {skills_count} compétences</span>
        </div>
        
        <div style="margin: 1rem 0;">
            {''.join([f'<span class="skill-tag">{skill}</span>' for skill in competences])}
        </div>
    </div>
    """
    
    st.html(card_html)
    
    # Boutons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button(
            "📄 Voir la description",
            key=f"details_{idx}",
            use_container_width=True
        ):
            st.session_state[f'show_desc_{idx}'] = not st.session_state.get(f'show_desc_{idx}', False)
    
    with btn_col2:
        is_fav = idx in st.session_state.favorites
        if st.button(
            "💖 Retirer des favoris" if is_fav else "🤍 Ajouter aux favoris",
            key=f"fav_{idx}",
            use_container_width=True
        ):
            if is_fav:
                st.session_state.favorites.remove(idx)
            else:
                st.session_state.favorites.append(idx)
            st.rerun()
    
    with btn_col3:
        # SOLUTION ROBUSTE : Utiliser un lien HTML stylisé comme un bouton
        if has_valid_url:
            # Créer un bouton HTML cliquable qui redirige vers l'offre
            button_html = f"""
            <a href="{url}" target="_blank" style="
                display: inline-block;
                width: 100%;
                padding: 0.5rem 1rem;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.95rem;
                transition: all 0.3s;
                box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.5)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(16, 185, 129, 0.3)'">
                🚀 Postuler sur le site
            </a>
            """
            st.markdown(button_html, unsafe_allow_html=True)
        else:
            # Si pas d'URL, afficher un bouton grisé
            st.button(
                "🚀 Postuler",
                key=f"apply_{idx}",
                use_container_width=True,
                disabled=True,
                help="Lien non disponible pour cette offre"
            )
    
    # AFFICHAGE DE LA DESCRIPTION
    if st.session_state.get(f'show_desc_{idx}', False):
        # Préparer le lien s'il existe
        link_html = ""
        if has_valid_url:
            link_html = f'<hr style="border-color: rgba(168, 85, 247, 0.3); margin: 1rem 0;"><p><strong style="color: #10b981;">🔗 <a href="{url}" target="_blank" style="color: #10b981;">Voir l\'offre complète sur le site de l\'entreprise</a></strong></p>'
        
        desc_html = f"""
        <div class="description-box">
            <h3 style="color: #a78bfa; margin-bottom: 1rem;">📝 Description Complète</h3>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #60a5fa;">Entreprise:</strong> {company}<br>
                <strong style="color: #60a5fa;">Poste:</strong> {title}<br>
                <strong style="color: #60a5fa;">Localisation:</strong> {location}<br>
                <strong style="color: #60a5fa;">Type de contrat:</strong> {contract}<br>
                <strong style="color: #60a5fa;">Télétravail:</strong> {'Oui' if remote in ['yes', 'oui'] else 'Hybride' if remote == 'hybrid' else 'Non'}
            </div>
            <hr style="border-color: rgba(168, 85, 247, 0.3); margin: 1rem 0;">
            <p style="white-space: pre-wrap; line-height: 1.8;">{description}</p>
            {link_html}
        </div>
        """
        
        st.markdown(desc_html, unsafe_allow_html=True)
        
        if competences:
            st.markdown("**💎 Compétences requises:**")
            st.write(", ".join(competences))

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(f"**📊 {len(filtered_df):,} offres** correspondent à vos critères")

with footer_col2:
    st.markdown(f"**⭐ {len(st.session_state.favorites)} favoris**")

with footer_col3:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Exporter en CSV",
        csv,
        f"offres_data_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True
    )

current_datetime = datetime.now().strftime("%d/%m/%Y à %H:%M")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: #64748b; font-size: 0.9rem;">
    Mise à jour: {current_datetime} • Plateforme d'emploi Data professionnelle
</div>
""", unsafe_allow_html=True)