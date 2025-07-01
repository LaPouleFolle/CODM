import streamlit as st
import random
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import plotly.graph_objects as go

# ----------------------
# Fonctions d'analyse
# ----------------------
def analyser_performance(kd_ratio, win_rate):
    if kd_ratio >= 3:
        niveau = " ga tu prends tes balles? en tout cas"
    elif kd_ratio >= 2:
        niveau = " Très bon joueur"
    elif kd_ratio >= 1:
        niveau = " Ton niveau est correcte mais tu es guezz quand même "
    else:
        niveau = "🛠 Besoin d'entraînement"

    conseils = []
    if win_rate < 50:
        conseils.append("Travaille ta communication en équipe frère c'est comment")
    if kd_ratio < 1:
        conseils.append("Teste d'autres armes plus stables vv")

    return niveau, conseils

def recommander_build(arme):
    equipements = {
        "DL Q33": "Silencieux Monolithique, FMJ, Poignée granuleuse, Viseur Tactique, Munitions étendues",
        "RPD": "Compensateur, Poignée lourde, Chargeur rapide, Laser OWC, Crosse tactique",
        "AK117": "Frein de bouche, Viseur Red Dot, Poignée verticale, Chargeur étendu, Atout Agilité",
        "Fennec": "Poignée .... , Laser tactique, Chargeur etendu A, Viseur point rouge",
        "Kilo 141": "Canon RTC long, Viseur classique, Crosse stable, Chargeur rapide, Laser OWC",
        "USS 9": "-----------------------------------------------",
        "VMP": "--------------------------------------------------",
        "Oden": "---------------------------------------------------",
        "etc": "",
    }
    return equipements.get(arme, "Aucun build trouvé. Essaie une arme plus populaire ga arrete d'être guezz.")

def strategie_par_map(mode, map_name):
    strategies = {
        "Multijoueur": {
            "Nuketown": " En vrai c'est une map pour jouer SMJ. Reste mobile, surveille les angles morts, spawn trap conseillé.",
            "Firing Range": " Utilise les angles. le sniper conseillé pour R&D sur les longues lignes oh, genre long A. Contrôle du middle essentiel également donc ne soit pas bête vv.",
            "Summit": " Utilise le top et les passages latéraux. La carte est également mieux pour les SMJ et idéalement les pompes, mais si tu veux utilise la mélé mdr.",
        },
        "Battle Royale": {
            "Black Market": " Je sais pas je joue pas br",
            "Dormitory": " --- ",
            "Launch Base": " ---- "
        },
    }
    return strategies.get(mode, {}).get(map_name, " Carte inconnue ou stratégie non disponible.")

# ----------------------
# Mon interface streamlit
# ----------------------
st.set_page_config(page_title="CODM Joueur Booster", layout="centered")
st.markdown("""
    <style>
        .main {
            background-color: #0d1117;
            color: #f1f1f1;
        }
        h1, h2, h3, .stTextInput>div>div>input {
            color: #facc15;
        }
        .stButton>button {
            background-color: #facc15;
            color: black;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("CODM - Booster vos performance (NB : je fais pas allusion au POUTOULOU voila)")
st.subheader("Analyse ton profil et reçois des conseils stratégiques ga !")

with st.form("stats_form"):
    pseudo = st.text_input("Ton pseudo CODM")
    kd_ratio = st.number_input("Ton K/D Ratio", min_value=0.0, step=0.01)
    win_rate = st.slider("Ton taux de victoire (%)", 0, 100, 50)
    reflexes = st.slider("Réflexes (1-10)", 1, 10, 5)
    strategy = st.slider("Stratégie (1-10)", 1, 10, 5)
    mobility = st.slider("Mobilité (1-10)", 1, 10, 5)
    arme_pref = st.text_input("Ton arme préférée ? (ex: DL Q33, RPD, AK117, Fennec, Kilo 141)")
    mode_pref = st.selectbox("Ton mode préféré", ["Multijoueur", "Battle Royale", "Zombie"])

    if mode_pref == "Multijoueur":
        map_pref = st.selectbox("Carte multijoueur", ["Nuketown", "Firing Range", "Summit", "Take Off", "Apocalyste", "Vacant", "Combine"])
    elif mode_pref == "Battle Royale":
        map_pref = st.selectbox("Zone de drop", ["Black Market", "Dormitory", "Launch Base"])
    else:
        map_pref = ""

    submit = st.form_submit_button("Analyser mon profil")

if submit:
    niveau, conseils = analyser_performance(kd_ratio, win_rate)
    st.success(f" Niveau estimé : {niveau}")

    if conseils:
        st.info(" Conseils personnalisés :")
        for c in conseils:
            st.write("-", c)

    st.divider()
    st.subheader("🔧 Recommandation de build pour ton arme")
    st.write(recommander_build(arme_pref))

    st.divider()
    st.subheader("Stratégie personnalisée selon ta carte")
    st.write(strategie_par_map(mode_pref, map_pref))

    st.divider()
    st.subheader("Radar de Compétences")
    categories = ['Réflexes', 'Stratégie', 'Mobilité']
    values = [reflexes, strategy, mobility]
    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(r=values + [values[0]],
                                    theta=categories + [categories[0]],
                                    fill='toself', name=pseudo))
    radar.update_layout(polar=dict(bgcolor="#1e1e1e"),
                        paper_bgcolor="#0d1117",
                        font_color="#facc15",
                        title="Carte Radar de Compétences")
    st.plotly_chart(radar, use_container_width=True)

    # Sauvegarde JSON pour suivi individuel
    stats_file = f"stats_{pseudo}.json"
    today = str(datetime.date.today())
    data_point = {"date": today, "kd": kd_ratio, "winrate": win_rate}
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            historique = json.load(f)
    else:
        historique = []
    historique.append(data_point)
    with open(stats_file, 'w') as f:
        json.dump(historique, f)

    # Graphe d'évolution K/D
    st.divider()
    st.subheader("Évolution de ton K/D dans le temps")
    dates = [x["date"] for x in historique]
    kds = [x["kd"] for x in historique]
    plt.figure(figsize=(10, 4))
    plt.plot(dates, kds, marker='o', linestyle='-', color='#facc15')
    plt.xlabel("Date")
    plt.ylabel("K/D Ratio")
    plt.title(f"Progression de {pseudo}")
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt.gcf())

    st.caption(f"Généré le {datetime.date.today()} • CODM Booster • Par Arsène le DEMON")
