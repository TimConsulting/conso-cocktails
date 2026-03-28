import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Planner", layout="centered")

# --- CHARGEMENT ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_RECETTES), pd.read_csv(URL_FORMATS)

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍹 Mes Courses")

# Sélecteurs principaux
cocktail = st.selectbox("Choisir une boisson", sorted(df_rec['Cocktail'].unique()))
pax = st.number_input("Nombre de PAX", min_value=1, value=50, step=5)

st.divider()

# Filtrage des ingrédients
ingredients = df_rec[df_rec['Cocktail'] == cocktail]

for _, row in ingredients.iterrows():
    nom_ing = row['Ingrédient']
    besoin_total = row['Quantité'] * pax
    unite = row['Unité']
    
    # Titre de l'ingrédient et besoin total
    st.subheader(f"{nom_ing} : {besoin_total} {unite}")
    
    formats = df_form[df_form['Ingrédient'] == nom_ing]
    total_selectionne = 0.0
    
    if not formats.empty:
        # Toggle pour ajuster (natif, toujours visible)
        ajuster = st.toggle(f"Ajuster {nom_ing}", key=f"tg_{nom_ing}")
        
        for i, (_, f) in enumerate(formats.iterrows()):
            suggestion = int(math.ceil(besoin_total / f['Contenance'])) if i == 0 else 0
            
            if ajuster:
                # Mode manuel avec sliders
                nb = st.slider(
                    f"{f['Marque']} ({f['Contenance']}{unite})",
                    0, 200, suggestion,
                    key=f"sld_{nom_ing}_{f['Marque']}"
                )
            else:
                # Mode automatique avec affichage simple
                nb = suggestion
                st.write(f"🔹 {f['Marque']} ({f['Contenance']}{unite}) : **{nb}**")
            
            total_selectionne += (nb * f['Contenance'])
        
        # Résumé du statut
        diff = total_selectionne - besoin_total
        if diff < 0:
            st.error(f"Manque {abs(round(diff,1))} {unite}")
        else:
            st.success(f"OK (+{round(diff,1)} {unite})")
    else:
        st.info("Aucun format disponible pour cet ingrédient.")
    
    st.divider() # Sépare nettement chaque ingrédient

st.caption("Données synchronisées avec Google Sheets")
