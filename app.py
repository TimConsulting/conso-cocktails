import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Planner", layout="centered")

# --- CSS (FIX VISIBILITÉ & ESPACEMENT) ---
st.markdown("""
    <style>
    .stApp { background-color: #F7F9FB; }
    
    /* Carte ingrédient avec marges ajustées */
    .ing-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 5px;      /* Réduit l'espace avant */
        margin-bottom: 35px;   /* Augmente l'espace après pour séparer du prochain */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
    }
    
    .ing-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
    }
    
    .qty-badge {
        background-color: #F0F2F6;
        color: #333;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .bottle-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed #EEE;
        font-size: 0.95rem;
    }

    .bottle-name { color: #555; flex: 1; margin-right: 10px; }
    
    .bottle-count { 
        font-weight: 700; 
        color: #FF4B4B; 
        background: #FFF0F0;
        padding: 2px 10px;
        border-radius: 6px;
        min-width: 35px;
        text-align: center;
    }

    .status-msg { 
        font-size: 0.85rem; 
        font-weight: 600; 
        margin-top: 15px; 
        padding-top: 10px; 
        border-top: 1px solid #F0F0F0;
    }
    .status-missing { color: #FF4B4B; }
    .status-ok { color: #28A745; }
    
    /* Espacement spécifique pour le toggle */
    .stCheckbox { margin-bottom: 15px; }
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
    
    # Début de la carte
    st.markdown(f'<div class="ing-card"><div class="ing-title"><span>{nom_ing}</span><span class="qty-badge">{besoin_total} {unite}</span></div>', unsafe_allow_html=True)
    
    formats = df_form[df_form['Ingrédient'] == nom_ing]
    total_selectionne = 0.0
    
    if not formats.empty:
        # Toggle placé AVANT le listing pour être bien visible
        ajuster = st.toggle(f"Ajuster {nom_ing}", key=f"tg_{nom_ing}")
        
        st.write("") # Petit espace

        for i, (_, f) in enumerate(formats.iterrows()):
            suggestion = int(math.ceil(besoin_total / f['Contenance'])) if i == 0 else 0
            
            if ajuster:
                nb = st.slider(
                    f"{f['Marque']} ({f['Contenance']}{unite})",
                    0, 200, suggestion,
                    key=f"sld_{nom_ing}_{f['Marque']}"
                )
            else:
                nb = suggestion
                st.markdown(f"""
                    <div class="bottle-line">
                        <span class="bottle-name">🔹 {f['Marque']} ({f['Contenance']}{unite})</span>
                        <span class="bottle-count">{nb}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            total_selectionne += (nb * f['Contenance'])
        
        # Pied de carte (Status)
        diff = total_selectionne - besoin_total
        if diff < 0:
            st.markdown(f'<div class="status-msg status-missing">❌ Manque {abs(round(diff,1))} {unite}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-msg status-ok">✅ OK (Reste {round(diff,1)} {unite})</div>', unsafe_allow_html=True)
    else:
        st.warning("Aucun format disponible.")
    
    # Fermeture de la div ing-card
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Données synchronisées avec Google Sheets")
