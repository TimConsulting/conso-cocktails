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
nb_cocktails = len(st.session_state.get('multiselect', []))
verres_txt = f"{int(total_verres/nb_cocktails)} par type" if nb_cocktails > 0 else "0"
st.info(f"🎯 **Total à servir : {int(total_verres)} verres** ({verres_txt})")

options = sorted(df_rec['Cocktail'].unique())
selection = st.multiselect("Cocktails à la carte", options, key="multiselect")

if selection:
    verres_par_type = total_verres / len(selection)
    
    tab1, tab2 = st.tabs(["🛒 Liste de Courses", "📖 Détail par Cocktail"])

    # --- VUE 1 : LISTE DE COURSES ---
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
            st.subheader(f"{nom_ing} ({round(besoin, 1)} {unite})")
            
            formats = df_form[df_form['Ingrédient'] == nom_ing]
            
            if not formats.empty:
                ajuster = st.toggle(f"Modifier {nom_ing}", key=f"tg_glob_{nom_ing}")
                for i, (_, f) in enumerate(formats.iterrows()):
                    sugg = int(math.ceil(besoin / f['Contenance'])) if i == 0 else 0
                    if ajuster:
                        st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, sugg, key=f"sld_glob_{nom_ing}_{f['Marque']}")
                    else:
                        st.write(f"🔹 {f['Marque']} : **{sugg}**")
            st.divider()

    # --- VUE 2 : DÉTAIL PAR COCKTAIL ---
    with tab2:
        for c in selection:
            with st.expander(f"Détail pour {c}", expanded=True):
                recette = df_rec[df_rec['Cocktail'] == c]
                for _, row in recette.iterrows():
                    ing_c = row['Ingrédient']
                    qty_c = row['Quantité'] * verres_par_type
                    unite_c = row['Unité']
                    
                    st.write(f"📍 **{ing_c}**")
                    
                    # On cherche la marque correspondante
                    f_info = df_form[df_form['Ingrédient'] == ing_c]
                    if not f_info.empty:
                        marque = f_info.iloc[0]['Marque']
                        cont = f_info.iloc[0]['Contenance']
                        st.markdown(f"Besoin : **{round(qty_c, 1)} {unite_c}**")
                        st.caption(f"Utiliser : **{marque}** ({cont}{unite_c})")
                    else:
                        st.markdown(f"Besoin : **{round(qty_c, 1)} {unite_c}**")

else:
    st.warning("Choisissez au moins un cocktail.")
