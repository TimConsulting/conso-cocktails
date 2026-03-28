import streamlit as st

import pandas as pd

import math


# --- CONFIGURATION MOBILE FIRST ---

st.set_page_config(page_title="Cocktail Calc", layout="centered")


# CSS pour améliorer le rendu sur téléphone

st.markdown("""

    <style>

    .main { background-color: #f8f9fa; }

    .stButton>button {

        width: 100%;

        border-radius: 10px;

        height: 3em;

        background-color: #FF4B4B;

        color: white;

        font-weight: bold;

    }

    .card {

        background-color: white;

        padding: 15px;

        border-radius: 10px;

        border-left: 5px solid #FF4B4B;

        margin-bottom: 10px;

        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);

    }

    </style>

    """, unsafe_allow_html=True)


# --- LIENS GOOGLE SHEET (A REMPLACER) ---

# Allez dans Fichier > Partager > Publier sur le web > CSV

URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"

URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"


@st.cache_data

def load_data():

    try:

        df_rec = pd.read_csv(URL_RECETTES)

        df_form = pd.read_csv(URL_FORMATS)

        return df_rec, df_form

    except:

        return None, None


df_rec, df_form = load_data()


# --- INTERFACE ---

st.title("🍸 Cocktail Planner")
st.write("Calculez vos courses en un clic.")


if df_rec is not None:

    # Sélection simplifiée pour mobile

    cocktail = st.selectbox("Sélectionnez le cocktail", df_rec['Cocktail'].unique())

    pax = st.number_input("Nombre d'invités (PAX)", min_value=1, value=50, step=5)


    if st.button("CALCULER LES COURSES"):

        st.divider()

        st.subheader(f"Pour {pax} {cocktail} :")
        

        # Filtrage

        besoins = df_rec[df_rec['Cocktail'] == cocktail]
        

        for _, row in besoins.iterrows():

            ing = row['Ingredient']

            total_cl = row['Quantite'] * pax

            unite = row['Unite']
            

            # Affichage de l'ingrédient dans une 
"carte"

            st.markdown(f"""<div class=\"card\">

                <small>{ing.upper()}</small><br>

                <b>Besoin total : {total_cl} {unite}</b>

            </div>""", unsafe_allow_html=True)
            

            # Calcul des formats de bouteilles

            formats_dispos = df_form[df_form['Ingredient'] == ing]
            

            if not formats_dispos.empty:

                cols = st.columns(len(formats_dispos))

                for i, (_, f) in enumerate(formats_dispos.iterrows()):

                    nb = math.ceil(total_cl / f['Contenance'])

                    cols[i].metric(label=f['Marque'], value=f"{nb} bout.")

            else:

                st.caption("⚠️ Aucun format de bouteille configuré.")
else:

    st.warning("👉 Veuillez configurer les liens Google Sheets dans le code.")
    st.info("Allez dans Fichier > Partager > Publier sur le web > Sélectionner l'onglet > Format CSV.")
