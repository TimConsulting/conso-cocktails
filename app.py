import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Planner", layout="centered")

# --- CSS (DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #F7F9FB; }
    .ing-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
    }
    .ing-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .qty-badge {
        background-color: #F0F2F6;
        color: #333;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-msg { font-size: 0.9rem; font-weight: 600; margin-top: 10px; }
    .status-missing { color: #FF4B4B; }
    .status-ok { color: #28A745; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_RECETTES), pd.read_csv(URL_FORMATS)

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍹 Mes Courses")

c1, c2 = st.columns([2, 1])
with c1:
    cocktail = st.selectbox("Boisson", sorted(df_rec['Cocktail'].unique()), label_visibility="collapsed")
with c2:
    pax = st.number_input("PAX", min_value=1, value=50, step=5, label_visibility="collapsed")

st.markdown("---")

ingredients = df_rec[df_rec['Cocktail'] == cocktail]

for _, row in ingredients.iterrows():
    nom_ing = row['Ingrédient']
    besoin_total = row['Quantité'] * pax
    unite = row['Unité']
    
    # Carte Ingrédient
    st.markdown(f'<div class="ing-card"><div class="ing-title"><span>{nom_ing}</span><span class="qty-badge">{besoin_total} {unite}</span></div>', unsafe_allow_html=True)
    
    formats = df_form[df_form['Ingrédient'] == nom_ing]
    total_selectionne = 0.0
    
    if not formats.empty:
        # Case à cocher pour activer les sliders
        ajuster = st.checkbox(f"Ajuster {nom_ing}", key=f"check_{nom_ing}")
        
        for i, (_, f) in enumerate(formats.iterrows()):
            # Calcul automatique suggéré (seulement sur le premier format par défaut)
            suggestion = int(math.ceil(besoin_total / f['Contenance'])) if i == 0 else 0
            
            if ajuster:
                # Si on ajuste, on affiche le slider (max 200)
                nb = st.slider(
                    f"{f['Marque']} ({f['Contenance']}{unite})",
                    0, 200, suggestion,
                    key=f"slider_{nom_ing}_{f['Marque']}"
                )
            else:
                # Si on n'ajuste pas, on prend la suggestion automatique
                nb = suggestion
                st.markdown(f"🔹 {f['Marque']} : **{nb}**")
            
            total_selectionne += (nb * f['Contenance'])
        
        # Feedback visuel
        diff = total_selectionne - besoin_total
        if diff < 0:
            st.markdown(f'<div class="status-msg status-missing">⚠️ Manque {abs(round(diff,2))} {unite}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-msg status-ok">✅ OK (Surplus {round(diff,2)} {unite})</div>', unsafe_allow_html=True)
    else:
        st.warning("Aucun format disponible.")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Données Google Sheets synchronisées.")
