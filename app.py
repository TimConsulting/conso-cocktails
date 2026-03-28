import streamlit as st
import pandas as pd
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="Cocktail Calculator", layout="centered")

# --- CHARGEMENT DES DONNÉES ---
URL_RECETTES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=0&single=true&output=csv"
URL_FORMATS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1qyomUyOvg9AU5gHgTTrufofoCT0fgOgJYA4xRJ5y5cHGnMDksjLOIvLF7y-m6UfoC_2kzTsotTal/pub?gid=663014863&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    df_r = pd.read_csv(URL_RECETTES)
    df_f = pd.read_csv(URL_FORMATS)
    # Nettoyage pour éviter les erreurs de type
    df_r['Quantité'] = pd.to_numeric(df_r['Quantité'], errors='coerce').fillna(0)
    df_f['Contenance'] = pd.to_numeric(df_f['Contenance'], errors='coerce').fillna(1)
    return df_r, df_f

df_rec, df_form = load_data()

# --- INTERFACE ENTRÉE ---
st.title("🍹 Cocktail Calculator")

pax_total = st.number_input("Nombre d'invités total", min_value=1, value=100, step=10)
options = sorted(df_rec['Cocktail'].unique())
selection = st.multiselect("Sélectionnez les cocktails", options)

repartition = {}
total_verres_evenement = 0

if selection:
    st.write("---")
    # Modification du libellé demandée
    st.write("**Nombre de verres par personne :**")
    
    cols = st.columns(len(selection))
    for i, c in enumerate(selection):
        with cols[i]:
            # Step à 1 pour rester sur des nombres entiers de verres
            nb_v = st.number_input(f"{c}", min_value=0, value=1, step=1, key=f"nb_{c}")
            repartition[c] = nb_v * pax_total
            total_verres_evenement += repartition[c]

    st.info(f"🎯 **Total à servir : {int(total_verres_evenement)} verres**")
    st.divider()

    # --- CALCUL DES BESOINS GLOBAUX ---
    cumul_global = {}
    for c in selection:
        verres_ce_cocktail = repartition[c]
        lignes = df_rec[df_rec['Cocktail'] == c]
        for _, row in lignes.iterrows():
            ing = row['Ingrédient']
            qty_unit = float(row['Quantité'])
            qty_totale = qty_unit * verres_ce_cocktail
            unite = str(row['Unité']) if not pd.isna(row['Unité']) else "unité"
            
            if ing in cumul_global:
                cumul_global[ing]['qty'] += qty_totale
            else:
                cumul_global[ing] = {'qty': qty_totale, 'unite': unite}

    tab1, tab2 = st.tabs(["🛒 Liste de Courses", "📖 Détail par Cocktail"])

    # --- VUE 1 : LISTE DE COURSES ---
    with tab1:
        stock_achete = {}
        
        for nom_ing, data in cumul_global.items():
            besoin_net = float(data['qty'])
            unite = str(data['unite'])
            
            st.markdown(f"### {nom_ing}")
            st.markdown(f"**BESOIN : `{round(besoin_net, 1)} {unite.upper()}`**")
            
            formats = df_form[df_form['Ingrédient'] == nom_ing]
            vol_ing_total = 0.0
            
            if not formats.empty:
                for i, (_, f) in enumerate(formats.iterrows()):
                    cont_f = float(f['Contenance'])
                    sugg = int(math.ceil(besoin_net / cont_f)) if i == 0 else 0
                    
                    # Key dynamique incluant 'sugg' pour forcer la mise à jour auto
                    nb = st.number_input(
                        f"{f['Marque']} ({cont_f}{unite})",
                        min_value=0, max_value=1000, value=sugg,
                        key=f"num_{nom_ing}_{f['Marque']}_{i}_{sugg}"
                    )
                    vol_ing_total += (nb * cont_f)
                
                stock_achete[nom_ing] = vol_ing_total
                
                diff = vol_ing_total - besoin_net
                if diff < -0.01: 
                    st.error(f"⚠️ Manque {abs(round(diff,1))} {unite}")
                else: 
                    st.caption(f"✅ Quantité couverte (Surplus : {round(diff,1)} {unite})")
            else:
                st.warning("Aucun format défini.")
                stock_achete[nom_ing] = 0
            st.divider()

    # --- VUE 2 : DÉTAIL PAR COCKTAIL ---
    with tab2:
        for c in selection:
            verres_prevus = repartition[c]
            with st.expander(f"Détail pour {c} ({int(verres_prevus)} verres)", expanded=True):
                st.markdown("**Recette (pour 1 verre) :**")
                lignes_c = df_rec[df_rec['Cocktail'] == c]
                for _, r in lignes_c.iterrows():
                    st.write(f"▪️ {r['Quantité']} {r['Unité']} {r['Ingrédient']}")
                
                st.divider()
                
                for _, row in lignes_c.iterrows():
                    ing_name = row['Ingrédient']
                    qty_theo = float(row['Quantité']) * verres_prevus
                    unite_name = str(row['Unité'])
                    
                    vol_total_dispo = stock_achete.get(ing_name, 0)
                    total_besoin_ing = cumul_global[ing_name]['qty']
                    ratio_poids = qty_theo / total_besoin_ing if total_besoin_ing > 0 else 0
                    part_dispo = vol_total_dispo * ratio_poids
                    
                    couleur = "green" if part_dispo >= (qty_theo - 0.05) else "red"
                    
                    st.write(f"📍 **{ing_name}**")
                    st.markdown(f"Besoin total : :{couleur}[**{round(part_dispo, 1)} {unite_name}**]")

else:
    st.warning("Sélectionnez au moins un cocktail pour commencer.")

st.write("")
st.caption("Application synchronisée avec Google Sheets.")
