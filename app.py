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

pax_total = st.number_input("Nombre d'invités total", min_value=1, value=50, step=5)
options = sorted(df_rec['Cocktail'].unique())
selection = st.multiselect("Sélectionnez les cocktails", options)

repartition = {}
total_verres_evenement = 0

if selection:
    st.write("---")
    st.write("**Nombre de verres par personne :**")
    cols = st.columns(len(selection))
    for i, c in enumerate(selection):
        with cols[i]:
            nb_v = st.number_input(f"{c}", min_value=0.0, value=1.0, step=0.5, key=f"nb_{c}")
            repartition[c] = nb_v * pax_total
            total_verres_evenement += repartition[c]

    st.info(f"🎯 **Total à servir : {int(total_verres_evenement)} verres**")
    st.divider()

    # --- CALCUL DES BESOINS GLOBAUX ---
    cumul_global = {}
    for c in selection:
        verres_pour_ce_cocktail = repartition[c]
        recette_data = df_rec[df_rec['Cocktail'] == c]
        for _, row in recette_data.iterrows():
            ing = row['Ingrédient']
            qty = row['Quantité'] * verres_pour_ce_cocktail
            unite = row['Unité']
            if ing in cumul_global:
                cumul_global[ing]['qty'] += qty
            else:
                cumul_global[ing] = {'qty': qty, 'unite': unite}

    tab1, tab2 = st.tabs(["🛒 Liste de Courses", "📖 Détail par Cocktail"])

    # --- VUE 1 : LISTE DE COURSES ---
    with tab1:
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
                    sugg = int(math.ceil(besoin / f['Contenance'])) if i == 0 else 0
                    if ajuster:
                        nb = st.slider(f"{f['Marque']} ({f['Contenance']}{unite})", 0, 200, sugg, key=f"sld_glob_{nom_ing}_{f['Marque']}")
                    else:
                        nb = sugg
                        st.write(f"🔹 {f['Marque']} : **{nb}**")
                    vol_ing_total += (nb * f['Contenance'])
                
                stock_achete[nom_ing] = vol_ing_total
                diff = vol_ing_total - besoin
                if diff < 0: st.error(f"Manque {abs(round(diff,1))} {unite}")
                else: st.success(f"OK (+{round(diff,1)})")
            st.divider()

    # --- VUE 2 : DÉTAIL PAR COCKTAIL ---
    with tab2:
        for c in selection:
            verres_prevus = repartition[c]
            with st.expander(f"Détail pour {c} ({int(verres_prevus)} verres)", expanded=True):
                
                # --- LOGIQUE RECETTE MULTI-LIGNES ---
                # On récupère toutes les lignes du cocktail
                lignes_cocktail = df_rec[df_rec['Cocktail'] == c]
                
                # On cherche la colonne Recette ou Préparation
                col_recette = 'Recette' if 'Recette' in df_rec.columns else 'Préparation'
                
                if col_recette in df_rec.columns:
                    # On récupère les textes uniques non vides de cette colonne pour ce cocktail
                    instructions = lignes_cocktail[col_recette].dropna().unique()
                    recette_complete = "\n\n".join(instructions) if len(instructions) > 0 else "Aucune instruction saisie."
                else:
                    recette_complete = "Colonne 'Recette' introuvable dans le Google Sheet."

                if st.button(f"📖 Voir la recette du {c}", key=f"btn_rec_{c}"):
                    st.info(f"**Méthode de préparation :**\n\n{recette_complete}")
                
                st.write("---")
                
                # Liste des ingrédients
                for _, row in lignes_cocktail.iterrows():
                    ing_c = row['Ingrédient']
                    qty_theo = row['Quantité'] * verres_prevus
                    unite_c = row['Unité']
                    
                    vol_total_dispo = stock_achete.get(ing_c, qty_theo)
                    ratio_poids = qty_theo / cumul_global[ing_c]['qty']
                    part_dispo = vol_total_dispo * ratio_poids
                    
                    couleur = "green" if part_dispo >= (qty_theo - 0.1) else "red"
                    st.write(f"📍 **{ing_c}**")
                    st.markdown(f"Besoin : :{couleur}[**{round(part_dispo, 1)} {unite_c}**]")
                    st.write("")

else:
    st.warning("Veuillez sélectionner au moins un cocktail.")
