import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Planner Pro", layout="centered")

# --- CHARGEMENT ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_RECETTES), pd.read_csv(URL_FORMATS)

df_rec, df_form = load_data()

# --- INTERFACE ---
st.title("🍹 Cocktail Planner")

# 1. PARAMÈTRES
col1, col2 = st.columns(2)
with col1:
    pax_total = st.number_input("Nombre d'invités", min_value=1, value=50, step=5)
with col2:
    ratio = st.number_input("Verres / personne", min_value=0.5, value=1.5, step=0.5)

total_verres = pax_total * ratio
options = sorted(df_rec['Cocktail'].unique())
selection = st.multiselect("Cocktails à la carte", options)

if selection:
    verres_par_type = total_verres / len(selection)
    
    # Création des deux onglets
    tab1, tab2 = st.tabs(["🛒 Liste par Ingrédients", "📖 Détail par Cocktail"])

    # --- VUE 1 : PAR INGRÉDIENTS (CUMULÉ POUR LES COURSES) ---
    with tab1:
        st.write(f"**Total à prévoir : {int(total_verres)} verres**")
        
        # Calcul du cumul global
        cumul_global = {}
        for c in selection:
            recette = df_rec[df_rec['Cocktail'] == c]
            for _, row in recette.iterrows():
                ing = row['Ingrédient']
                qty = row['Quantité'] * verres_par_type
                unite = row['Unité']
                if ing in cumul_global:
                    cumul_global[ing]['qty'] += qty
                else:
                    cumul_global[ing] = {'qty': qty, 'unite': unite}

        for nom_ing, data in cumul_global.items():
            besoin = data['qty']
            unite = data['unite']
            
            st.subheader(f"{nom_ing} ({round(besoin, 1)} {unite})")
            
            formats = df_form[df_form['Ingrédient'] == nom_ing]
            total_sel = 0.0
            
            if not formats.empty:
                ajuster = st.toggle(f"Ajuster {nom_ing}", key=f"tg_glob_{nom_ing}")
                
                for i, (_, f) in enumerate(formats.iterrows()):
                    sugg = int(math.ceil(besoin / f['Contenance'])) if i == 0 else 0
                    if ajuster:
                        nb = st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, sugg, key=f"sld_glob_{nom_ing}_{f['Marque']}")
                    else:
                        nb = sugg
                        st.write(f"🔹 {f['Marque']} : **{nb}**")
                    total_sel += (nb * f['Contenance'])
                
                # Statut
                diff = total_sel - besoin
                if diff < 0: st.error(f"Manque {abs(round(diff,1))} {unite}")
                else: st.success(f"OK (+{round(diff,1)})")
            st.divider()

    # --- VUE 2 : PAR COCKTAIL (POUR LA PRÉPARATION) ---
    with tab2:
        st.write(f"**Répartition : {int(verres_par_type)} verres par cocktail**")
        for c in selection:
            with st.expander(f"Détail pour {c}", expanded=True):
                recette = df_rec[df_rec['Cocktail'] == c]
                for _, row in recette.iterrows():
                    ing_c = row['Ingrédient']
                    qty_c = row['Quantité'] * verres_par_type
                    unite_c = row['Unité']
                    
                    # On affiche juste le besoin net ici pour ne pas alourdir
                    st.write(f"📍 **{ing_c}** : {round(qty_c, 1)} {unite_c}")
                    
                    # Petit rappel du format principal pour info
                    f_principal = df_form[df_form['Ingrédient'] == ing_c]
                    if not f_principal.empty:
                        f1 = f_principal.iloc[0]
                        nb_f1 = math.ceil(qty_c / f1['Contenance'])
                        st.caption(f"Soit environ {nb_f1} bouteilles de {f1['Marque']}")

else:
    st.warning("Choisissez au moins un cocktail pour voir les calculs.")
