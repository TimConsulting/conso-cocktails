import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Planner Multi", layout="centered")

# --- CHARGEMENT ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_RECETTES), pd.read_csv(URL_FORMATS)

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍹 Planning de l'Événement")

# 1. PARAMÈTRES GLOBAUX
col1, col2 = st.columns(2)
with col1:
    pax_total = st.number_input("Nombre d'invités total", min_value=1, value=50, step=5)
with col2:
    ratio = st.number_input("Cocktails par personne", min_value=0.5, value=1.5, step=0.5)

total_verres_attendus = pax_total * ratio
st.info(f"Prévision totale : **{int(total_verres_attendus)} verres** à servir.")

# 2. CHOIX DES COCKTAILS
options = sorted(df_rec['Cocktail'].unique())
selection_cocktails = st.multiselect("Quels cocktails proposez-vous ?", options)

if selection_cocktails:
    st.divider()
    
    # Calcul de la part de chaque cocktail (répartition égale)
    nb_types = len(selection_cocktails)
    verres_par_type = total_verres_attendus / nb_types
    
    # AGGRÉGATION DES INGRÉDIENTS
    # On crée un dictionnaire pour cumuler les besoins si un ingrédient est dans plusieurs cocktails
    cumul_besoins = {} # { 'Nom' : {'quantite': X, 'unite': Y} }

    for c in selection_cocktails:
        recette = df_rec[df_rec['Cocktail'] == c]
        for _, row in recette.iterrows():
            ing = row['Ingrédient']
            qty = row['Quantité'] * verres_par_type
            unite = row['Unité']
            
            if ing in cumul_besoins:
                cumul_besoins[ing]['quantite'] += qty
            else:
                cumul_besoins[ing] = {'quantite': qty, 'unite': unite}

    # 3. AFFICHAGE DES BESOINS CUMULÉS
    for nom_ing, data in cumul_besoins.items():
        besoin_total = data['quantite']
        unite = data['unite']
        
        st.subheader(f"{nom_ing} : {round(besoin_total, 1)} {unite}")
        
        # Formats disponibles
        formats = df_form[df_form['Ingrédient'] == nom_ing]
        
        if not formats.empty:
            ajuster = st.toggle(f"Ajuster {nom_ing}", key=f"tg_{nom_ing}")
            total_selectionne = 0.0
            
            for i, (_, f) in enumerate(formats.iterrows()):
                # Suggestion auto basée sur le premier format
                suggestion = int(math.ceil(besoin_total / f['Contenance'])) if i == 0 else 0
                
                if ajuster:
                    nb = st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, suggestion, key=f"sld_{nom_ing}_{f['Marque']}")
                else:
                    nb = suggestion
                    st.write(f"🔹 {f['Marque']} : **{nb}**")
                
                total_selectionne += (nb * f['Contenance'])
            
            # Statut
            diff = total_selectionne - besoin_total
            if diff < 0:
                st.error(f"Manque {abs(round(diff,1))} {unite}")
            else:
                st.success(f"OK (+{round(diff,1)} {unite})")
        else:
            st.warning("Aucun format disponible.")
        
        st.divider()

else:
    st.warning("Veuillez sélectionner au moins un cocktail.")

st.caption("Le calcul répartit équitablement le nombre de verres entre les cocktails choisis.")
