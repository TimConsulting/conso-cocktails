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

# --- INTERFACE ENTRÉE ---
st.title("🍹 Cocktail Planner")

col1, col2 = st.columns(2)
with col1:
    pax_total = st.number_input("Nombre d'invités", min_value=1, value=50, step=5)
with col2:
    ratio = st.number_input("Verres / personne", min_value=0.5, value=1.5, step=0.5)

total_verres = pax_total * ratio
nb_sel = len(st.session_state.get('multiselect', []))
verres_txt = f"{int(total_verres/nb_sel)} par type" if nb_sel > 0 else "0"
st.info(f"🎯 **Total à servir : {int(total_verres)} verres** ({verres_txt})")

selection = st.multiselect("Cocktails à la carte", sorted(df_rec['Cocktail'].unique()), key="multiselect")

if selection:
    verres_par_type = total_verres / len(selection)
    
    # --- CALCUL DES BESOINS GLOBAUX ---
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

    tab1, tab2 = st.tabs(["🛒 Liste de Courses", "📖 Détail par Cocktail"])

    # --- VUE 1 : LISTE DE COURSES (Définit les quantités) ---
    with tab1:
        # On crée un dictionnaire pour stocker ce qu'on "achète" réellement
        stock_achete = {}

        for nom_ing, data in cumul_global.items():
            besoin = data['qty']
            unite = data['unite']
            st.subheader(f"{nom_ing} ({round(besoin, 1)} {unite})")
            
            formats = df_form[df_form['Ingrédient'] == nom_ing]
            vol_ing_total = 0.0
            
            if not formats.empty:
                ajuster = st.toggle(f"Modifier {nom_ing}", key=f"tg_glob_{nom_ing}")
                
                for i, (_, f) in enumerate(formats.iterrows()):
                    # Calcul automatique de base
                    sugg = int(math.ceil(besoin / f['Contenance'])) if i == 0 else 0
                    
                    if ajuster:
                        nb = st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, sugg, key=f"sld_glob_{nom_ing}_{f['Marque']}")
                    else:
                        nb = sugg
                        st.write(f"🔹 {f['Marque']} : **{nb}**")
                    
                    vol_ing_total += (nb * f['Contenance'])
                
                # ON ENREGISTRE LE VOLUME CHOISI
                stock_achete[nom_ing] = vol_ing_total
                
                diff = vol_ing_total - besoin
                if diff < 0: st.error(f"Manque {abs(round(diff,1))} {unite}")
                else: st.success(f"OK (+{round(diff,1)})")
            st.divider()

    # --- VUE 2 : DÉTAIL PAR COCKTAIL (Utilise les données de l'onglet 1) ---
    with tab2:
        for c in selection:
            with st.expander(f"Détail pour {c}", expanded=True):
                recette = df_rec[df_rec['Cocktail'] == c]
                for _, row in recette.iterrows():
                    ing_c = row['Ingrédient']
                    qty_theo = row['Quantité'] * verres_par_type
                    unite_c = row['Unité']
                    
                    # On récupère le volume "acheté" dans l'onglet 1
                    # Si pas d'ajustement, on prend le théorique par défaut
                    vol_total_dispo = stock_achete.get(ing_c, qty_theo)
                    
                    # On calcule la part de ce cocktail (au prorata)
                    part_cocktail = vol_total_dispo / len(selection)
                    
                    st.write(f"📍 **{ing_c}**")
                    
                    f_info = df_form[df_form['Ingrédient'] == ing_c]
                    if not f_info.empty:
                        marque = f_info.iloc[0]['Marque']
                        cont = f_info.iloc[0]['Contenance']
                        
                        # Affichage du besoin mis à jour selon les bouteilles achetées
                        couleur = "green" if part_cocktail >= (qty_theo - 0.1) else "red"
                        st.markdown(f"Besoin : :{couleur}[**{round(part_cocktail, 1)} {unite_c}**] (disponible)")
                        st.caption(f"Utiliser : **{marque}** ({cont}{unite_c})")
                    else:
                        st.markdown(f"Besoin : **{round(qty_theo, 1)} {unite_c}**")
                    st.write("")
else:
    st.warning("Choisissez au moins un cocktail.")
