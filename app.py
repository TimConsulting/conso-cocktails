import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Cocktail Planner", layout="centered")

# Style CSS pour une interface "Mobile First"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border: none;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #FF4B4B;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .ing-name {
        color: #7f8c8d;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .qty-text {
        color: #2c3e50;
        font-size: 1.2em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIENS GOOGLE SHEET ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60) # Rafraîchit les données toutes les minutes
def load_data():
    try:
        df_rec = pd.read_csv(URL_RECETTES)
        df_form = pd.read_csv(URL_FORMATS)
        # Nettoyage rapide des espaces inutiles dans les noms
        df_rec['Cocktail'] = df_rec['Cocktail'].str.strip()
        df_rec['Ingredient'] = df_rec['Ingredient'].str.strip()
        df_form['Ingredient'] = df_form['Ingredient'].str.strip()
        return df_rec, df_form
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return None, None

df_rec, df_form = load_data()

# --- INTERFACE UTILISATEUR ---
st.title("🍸 Cocktail Planner")
st.write("Préparez vos événements en un clin d'œil.")

if df_rec is not None and df_form is not None:
    # 1. Entrées utilisateur
    cocktail_list = sorted(df_rec['Cocktail'].unique())
    cocktail_choisi = st.selectbox("Choisissez un cocktail", cocktail_list)
    pax = st.number_input("Nombre d'invités (PAX)", min_value=1, value=50, step=1)

    st.markdown("---")

    if st.button("CALCULER LES COURSES"):
        st.header(f"Besoins pour {pax} {cocktail_choisi}")
        
        # Filtrer les ingrédients de la recette
        ingredients_recette = df_rec[df_rec['Cocktail'] == cocktail_choisi]
        
        for _, row in ingredients_recette.iterrows():
            nom_ing = row['Ingredient']
            qty_par_verre = row['Quantite']
            unite = row['Unite']
            besoin_total = qty_par_verre * pax
            
            # Affichage de la carte d'ingrédient
            st.markdown(f"""
                <div class="card">
                    <div class="ing-name">{nom_ing}</div>
                    <div class="qty-text">Total : {besoin_total} {unite}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Recherche des formats de bouteilles correspondants
            formats_dispos = df_form[df_form['Ingredient'] == nom_ing]
            
            if not formats_dispos.empty:
                cols = st.columns(len(formats_dispos))
                for i, (_, f) in enumerate(formats_dispos.iterrows()):
                    # Calcul du nombre de bouteilles (arrondi au supérieur)
                    nb_bouteilles = math.ceil(besoin_total / f['Contenance'])
                    with cols[i]:
                        st.metric(label=f['Marque'], value=f"{nb_bouteilles}")
                        st.caption(f"en {f['Contenance']} {f['Unite']}")
            else:
                st.info(f"💡 Aucun format défini pour {nom_ing}")
else:
    st.error("⚠️ Impossible de lire le Google Sheet. Vérifiez la publication au format CSV.")

# Pied de page discret
st.markdown("---")
st.caption("Modifiez vos recettes et formats directement dans Google Sheets pour mettre à jour cette liste.")
