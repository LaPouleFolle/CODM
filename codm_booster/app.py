import streamlit as st
import random
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

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
        "Fennec": "Poignée ergonomique, Laser tactique, Chargeur grande capacité, Viseur point rouge",
        "Kilo 141": "Canon RTC long, Viseur classique, Crosse stable, Chargeur rapide, Laser OWC",
        "USS 9": "-----------------------------------------------",
        "VMP": "--------------------------------------------------",
        "Oden": "---------------------------------------------------", "etc": "",
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
# Interface Streamlit
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

st.title("🪖 CODM Joueur Booster")
st.subheader("Analyse ton profil et reçois des conseils stratégiques ga !")

with st.form("stats_form"):
    pseudo = st.text_input("Ton pseudo CODM")
    kd_ratio = st.number_input("Ton K/D Ratio", min_value=0.0, step=0.01)
    win_rate = st.slider("Ton taux de victoire (%)", 0, 100, 50)
    arme_pref = st.text_input("Ton arme préférée ? (ex: DL Q33, RPD, AK117, Fennec, Kilo 141)")
    mode_pref = st.selectbox("Ton mode préféré", ["Multijoueur", "Battle Royale", "Zombie"])

    if mode_pref == "Multijoueur":
        map_pref = st.selectbox("Carte multijoueur", ["Nuketown", "Firing Range", "Summit", "Take Off", "Apocalyste","Vacant", "Combine"])
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

    # Enregistrement dans CSV
    stats_file = "stats_codm.csv"
    new_data = pd.DataFrame([{
        "Date": datetime.date.today(),
        "Pseudo": pseudo,
        "K/D": kd_ratio,
        "WinRate": win_rate,
        "Arme": arme_pref,
        "Mode": mode_pref,
        "Carte": map_pref
    }])
    if os.path.exists(stats_file):
        old_data = pd.read_csv(stats_file)
        all_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        all_data = new_data
    all_data.to_csv(stats_file, index=False)

    st.divider()
    st.subheader("📊 Évolution de ton K/D dans le temps")
    if os.path.exists(stats_file):
        df = pd.read_csv(stats_file)
        df_filtered = df[df["Pseudo"] == pseudo]
        if not df_filtered.empty:
            df_filtered["Date"] = pd.to_datetime(df_filtered["Date"])
            df_filtered = df_filtered.sort_values("Date")
            plt.plot(df_filtered["Date"], df_filtered["K/D"], marker='o')
            plt.title(f"Progression K/D de {pseudo}")
            plt.xlabel("Date")
            plt.ylabel("K/D Ratio")
            plt.xticks(rotation=45)
            st.pyplot(plt.gcf())
        else:
            st.write("Aucune donnée trouvée pour ce pseudo.")

    st.caption(f"Généré le {datetime.date.today()} • Version CODM Booster • Par Arsène le DEMON ")
