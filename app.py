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
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #FF4B4B;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .ing-name {
        color: #7f8c8d;
        font-size: 0.85em;
        text-transform: uppercase;
        font-weight: bold;
    }
    .qty-text {
        color: #2c3e50;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIENS GOOGLE SHEET ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        # Lecture avec gestion des noms de colonnes précis
        df_rec = pd.read_csv(URL_RECETTES)
        df_form = pd.read_csv(URL_FORMATS)
        
        # Nettoyage des colonnes (suppression des espaces vides autour des noms)
        for df in [df_rec, df_form]:
            df.columns = df.columns.str.strip()
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()
                
        return df_rec, df_form
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return None, None

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍸 Cocktail Planner")
st.write("Calculez vos bouteilles instantanément.")

if df_rec is not None and df_form is not None:
    # 1. Entrées
    cocktails_disponibles = sorted(df_rec['Cocktail'].unique())
    cocktail_choisi = st.selectbox("Sélectionnez le cocktail", cocktails_disponibles)
    pax = st.number_input("Nombre d'invités (PAX)", min_value=1, value=50, step=1)

    st.markdown("---")

    if st.button("VOIR MA LISTE DE COURSES"):
        st.header(f"Calcul pour {pax} {cocktail_choisi}")
        
        # Filtrer les ingrédients de la recette choisie
        ingredients_recette = df_rec[df_rec['Cocktail'] == cocktail_choisi]
        
        for _, row in ingredients_recette.iterrows():
            nom_ing = row['Ingrédient']
            qty_unitaire = row['Quantité']
            unite = row['Unité']
            besoin_total = qty_unitaire * pax
            
            # Affichage de la ligne d'ingrédient
            st.markdown(f"""
                <div class="card">
                    <div class="ing-name">{nom_ing}</div>
                    <div class="qty-text"><b>Besoin : {besoin_total} {unite}</b></div>
                </div>
            """, unsafe_allow_html=True)
            
            # Recherche des formats correspondants dans l'autre feuille
            formats_dispos = df_form[df_form['Ingrédient'] == nom_ing]
            
            if not formats_dispos.empty:
                cols = st.columns(len(formats_dispos))
                for i, (_, f) in enumerate(formats_dispos.iterrows()):
                    # Calcul : Besoin / Contenance, arrondi au supérieur
                    try:
                        nb_bout = math.ceil(besoin_total / float(f['Contenance']))
                        with cols[i]:
                            st.metric(label=f"{f['Marque']}", value=f"{nb_bout}")
                            st.caption(f"Format {f['Contenance']}{f['Unité']}")
                    except:
                        st.caption("Erreur de calcul sur ce format")
            else:
                st.info(f"💡 Ajoutez des marques pour '{nom_ing}' dans l'onglet Formats.")
else:
    st.info("Vérifiez que votre Google Sheet est bien publié en CSV et contient les bons en-têtes.")

st.markdown("---")
st.caption("Données synchronisées avec Google Sheets")
