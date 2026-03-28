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
# Affichage du bandeau informatif que tu aimais bien
st.info(f"🎯 **Total à servir : {int(total_verres)} verres** ({int(total_verres/len(st.session_state.get('multiselect', [1]))) if st.session_state.get('multiselect') else 0} par type)")

options = sorted(df_rec['Cocktail'].unique())
selection = st.multiselect("Cocktails à la carte", options, key="multiselect")

if selection:
    verres_par_type = total_verres / len(selection)
    
    # Dictionnaire pour stocker les ajustements réels faits par l'utilisateur
    ajustements_reels = {} 

    tab1, tab2 = st.tabs(["🛒 Liste de Courses", "📖 Détail par Cocktail"])

    # --- VUE 1 : LISTE DE COURSES (Source de vérité) ---
    with tab1:
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
            st.subheader(f"{nom_ing} (Besoin : {round(besoin, 1)} {unite})")
            
            formats = df_form[df_form['Ingrédient'] == nom_ing]
            vol_total_choisi = 0.0
            
            if not formats.empty:
                ajuster = st.toggle(f"Modifier {nom_ing}", key=f"tg_glob_{nom_ing}")
                
                for i, (_, f) in enumerate(formats.iterrows()):
                    sugg = int(math.ceil(besoin / f['Contenance'])) if i == 0 else 0
                    if ajuster:
                        nb = st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, sugg, key=f"sld_glob_{nom_ing}_{f['Marque']}")
                    else:
                        nb = sugg
                        st.write(f"🔹 {f['Marque']} : **{nb}**")
                    vol_total_choisi += (nb * f['Contenance'])
                
                # Sauvegarde du volume réellement choisi pour la vue 2
                ajustements_reels[nom_ing] = vol_total_choisi
                
                diff = vol_total_choisi - besoin
                if diff < 0: st.error(f"Manque {abs(round(diff,1))} {unite}")
                else: st.success(f"OK (+{round(diff,1)})")
            st.divider()

    # --- VUE 2 : DÉTAIL PAR COCKTAIL (Synchronisée) ---
    with tab2:
        for c in selection:
            with st.expander(f"Détail pour {c}", expanded=True):
                recette = df_rec[df_rec['Cocktail'] == c]
                for _, row in recette.iterrows():
                    ing_c = row['Ingrédient']
                    qty_theorique = row['Quantité'] * verres_par_type
                    unite_c = row['Unité']
                    
                    # On récupère ce qui a été choisi dans l'onglet 1
                    vol_achete = ajustements_reels.get(ing_c, qty_theorique)
                    
                    # Calcul de la part proportionnelle pour ce cocktail précis
                    # Si on a acheté plus ou moins, on montre ce que ça donne par cocktail
                    st.write(f"📍 **{ing_c}**")
                    col_a, col_b = st.columns(2)
                    col_a.caption(f"Théorique : {round(qty_theorique, 1)} {unite_c}")
                    
                    # Couleur du texte selon si on a assez acheté
                    couleur = "green" if vol_achete >= (cumul_global[ing_c]['qty'] - 0.1) else "red"
                    col_b.markdown(f"**Acheté : :{couleur}[{round(vol_achete / len(selection), 1)} {unite_c}]**")

else:
    st.warning("Choisissez au moins un cocktail.")
