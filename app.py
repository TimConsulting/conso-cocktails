import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Cocktail Planner", layout="centered")

# --- CSS PERSONNALISÉ (DESIGN MOBILE APP) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #F7F9FB; }
    
    /* Titres et sections */
    h1 { color: #1E1E1E; font-family: 'Inter', sans-serif; font-weight: 800; text-align: center; }
    
    /* Cartes pour chaque ingrédient */
    .ing-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
    }
    
    /* Header de l'ingrédient */
    .ing-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }

    /* Badge de quantité */
    .qty-badge {
        background-color: #F0F2F6;
        color: #333;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Status (Manque/OK) */
    .status-msg { font-size: 0.9rem; font-weight: 600; margin-top: 10px; }
    .status-missing { color: #FF4B4B; }
    .status-ok { color: #28A745; }

    /* Cacher les labels redondants des sliders */
    div[data-testid="stSlider"] label { font-size: 0.85rem; color: #666; }
    
    /* Espace entre les lignes */
    hr { margin: 2rem 0; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_RECETTES), pd.read_csv(URL_FORMATS)

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍹 Mes Courses")

# Sélecteurs principaux
c1, c2 = st.columns([2, 1])
with c1:
    cocktail = st.selectbox("Boisson", sorted(df_rec['Cocktail'].unique()), label_visibility="collapsed")
with c2:
    pax = st.number_input("PAX", min_value=1, value=50, step=5, label_visibility="collapsed")

st.markdown("---")

# Filtrage
ingredients = df_rec[df_rec['Cocktail'] == cocktail]

for _, row in ingredients.iterrows():
    nom_ing = row['Ingrédient']
    besoin_total = row['Quantité'] * pax
    unite = row['Unité']
    
    # Début de la carte ingrédient
    st.markdown(f"""
    <div class="ing-card">
        <div class="ing-title">
            <span>{nom_ing}</span>
            <span class="qty-badge">{besoin_total} {unite}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Recherche des formats
    formats = df_form[df_form['Ingrédient'] == nom_ing]
    
    total_selectionne = 0.0
    
    if not formats.empty:
        # On affiche un slider par format
        for i, (_, f) in enumerate(formats.iterrows()):
            # Suggestion automatique : Si c'est le premier format, on pré-remplit
            suggestion = 0
            if i == 0: 
                suggestion = int(math.ceil(besoin_total / f['Contenance']))
            
            # Affichage du slider
            nb = st.slider(
                f"{f['Marque']} ({f['Contenance']}{unite})",
                0, int(suggestion + 5), suggestion,
                key=f"{nom_ing}_{f['Marque']}"
            )
            total_selectionne += (nb * f['Contenance'])
        
        # État du calcul
        diff = total_selectionne - besoin_total
        if diff < 0:
            st.markdown(f'<div class="status-msg status-missing">⚠️ Manque {abs(diff)} {unite}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-msg status-ok">✅ OK (Surplus {diff} {unite})</div>', unsafe_allow_html=True)
    else:
        st.warning("Aucune marque en stock.")
    
    # Fin de la carte
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Données à jour selon le Google Sheet")
