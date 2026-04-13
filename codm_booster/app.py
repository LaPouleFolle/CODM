import streamlit as st
import random
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import plotly.graph_objects as go
import sqlite3

# configuration de ma page
st.set_page_config(page_title="CODM Joueur Booster", layout="centered")

# ----------------------
# Gestion de la base de donnée ( c'est le plus important)
# ----------------------
def init_db():
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS performances 
                 (pseudo TEXT, kd REAL, winrate INTEGER, date TEXT)''')
    conn.commit()
    conn.close()

def sauvegarder_stats_sql(pseudo, kd, winrate):
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    c = conn.cursor()
    today = str(datetime.date.today())
    c.execute("INSERT INTO performances (pseudo, kd, winrate, date) VALUES (?, ?, ?, ?)", 
              (pseudo, kd, winrate, today))
    conn.commit()
    conn.close()

init_db()

# ----------------------
# Les fonctions d'analyse (calcul simple)
# ----------------------
def analyser_performance(kd_ratio, win_rate):
    if kd_ratio >= 3:
        niveau = " ga tu prends tes balles? en tout cas"
    elif kd_ratio >= 2:
        niveau = " Très bon joueur"
    elif kd_ratio >= 1:
        niveau = " Ton niveau est correcte mais tu es guezz quand même "
    else:
        niveau = "Besoin d'entraînement"
    
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
    }
    return equipements.get(arme, "Aucun build trouvé. Essaie une arme plus populaire ga.")

def strategie_par_map(mode, map_name):
    strategies = {
        "Multijoueur": {
            "Nuketown": " En vrai c'est une map pour jouer SMJ. Reste mobile, spawn trap conseillé.",
            "Firing Range": " Utilise les angles. sniper conseillé pour R&D sur les longues lignes.",
            "Summit": " Utilise le top et les passages latéraux. Idéal pour les SMJ.",
        },
        "Battle Royale": {
            "Black Market": " Je sais pas je joue pas br",
        },
    }
    return strategies.get(mode, {}).get(map_name, " Stratégie non disponible.")

# ----------------------
# Ici je gere le style de la page ( les couleurs)
# ----------------------
st.markdown("""
    <style>
        /* Fond Noir Profond */
        .stApp {
            background-color: #0F0F0F;
        }

        /* Titres en Orange Brûlé */
        h1, h2, h3, label {
            color: #FF4D00 !important;
            font-family: 'Black Ops One', cursive, sans-serif; /* Style militaire si dispo */
        }

        /* Texte secondaire en Blanc */
        p, .stMarkdown {
            color: #FFFFFF !important;
        }

        /* Champs de saisie sombres avec bordure Orange */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
            border: 1px solid #FF4D00 !important;
        }

        /* Bouton Orange avec effet de survol */
        .stButton>button {
            background-color: #FF4D00;
            color: white;
            font-weight: bold;
            border-radius: 4px;
            border: none;
            text-transform: uppercase;
            width: 100%;
        }

        .stButton>button:hover {
            background-color: #CC3D00;
            color: #FFFFFF;
            box-shadow: 0px 0px 15px #FF4D00;
        }

        /* Barre d'onglets personnalisée */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1A1A1A;
        }
        .stTabs [data-baseweb="tab"] {
            color: #888888;
        }
        .stTabs [aria-selected="true"] {
            color: #FF4D00 !important;
            border-bottom-color: #FF4D00 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("CODM BOOSTER PRO")

# ----------------------
# Création des onglets
# ----------------------
tab_home, tab_analyse, tab_media = st.tabs(["Accueil", "Analyse & Stats", "📺 Communauté & Live"])

# --- Onglet 1 : accueil ---
with tab_home:
    st.markdown("""
        <div style="background-color: #0369A1; padding: 20px; border-radius: 15px; text-align: center;">
            <h2 style="color: white !important;">Bienvenue sur CODM Booster</h2>
            <p style="color: #BAE6FD !important;">Le site qui te permet d'analyser tes performances et bien d'autre (par SK DEMON)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats rapides de la base SQL
    conn = sqlite3.connect("codm_data.db")
    df_home = pd.read_sql_query("SELECT kd FROM performances", conn)
    conn.close()
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Analyses effectuées", len(df_home))
    with c2:
        if not df_home.empty:
            st.metric("Moyenne K/D Global", f"{df_home['kd'].mean():.2f}")
    
    st.image("https://png.pngtree.com/background/20231101/original/pngtree-3d-illustration-of-blue-background-with-digital-binary-code-picture-image_5829125.jpg", use_container_width=True)
    st.info("💡 Conseil : Va dans l'onglet 'Analyse' pour enregistrer ton profil.")

    st.subheader("🏆 Top Global Démon")
    conn = sqlite3.connect("codm_data.db")
    df_top = pd.read_sql_query("SELECT pseudo, MAX(kd) as kd FROM performances GROUP BY pseudo ORDER BY kd DESC LIMIT 5", conn)
    st.table(df_top)
    conn.close()
# --- Onglet 2 : analyse 
with tab_analyse:
    st.header("Analyse ton Skill")
    
    with st.form("stats_form"):
        pseudo = st.text_input("Ton pseudo CODM")
        kd_ratio = st.number_input("Ton K/D Ratio", min_value=0.0, step=0.01)
        win_rate = st.slider("Ton taux de victoire (%)", 0, 100, 50)
        arme_pref = st.text_input("Ton arme préférée ?")
        mode_pref = st.selectbox("Ton mode préféré", ["Multijoueur", "Battle Royale"])
        
        if mode_pref == "Multijoueur":
            map_pref = st.selectbox("Carte", ["Nuketown", "Firing Range", "Summit"])
        else:
            map_pref = st.selectbox("Zone", ["Black Market"])
            
        submit = st.form_submit_button("Analyser mon profil")

    if submit:
        if pseudo.strip(): 
            sauvegarder_stats_sql(pseudo, kd_ratio, win_rate)
        else:
            st.error("Mets un pseudo ga !")
            st.stop()

        niveau, conseils = analyser_performance(kd_ratio, win_rate)
        st.success(f"Niveau estimé : {niveau}")
        
        for c in conseils:
            st.write("-", c)

        st.divider()
        st.subheader("🔧 Build recommandé")
        st.write(recommander_build(arme_pref))
        
        st.subheader("🗺️ Stratégie de carte")
        st.write(strategie_par_map(mode_pref, map_pref))

        # Gestion Historique JSON
        stats_file = f"stats_{pseudo}.json"
        data_point = {"date": str(datetime.date.today()), "kd": kd_ratio, "winrate": win_rate}
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                historique = json.load(f)
        else:
            historique = []
        historique.append(data_point)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(historique, f, ensure_ascii=False)

        # Graphique
        st.divider()
        st.subheader("Évolution du K/D")
        dates = [x["date"] for x in historique]
        kds = [x["kd"] for x in historique]
        fig, ax = plt.subplots()
        ax.plot(dates, kds, marker='o', color='#0369A1')
        plt.xticks(rotation=45)
        st.pyplot(fig)

# --- Onglet 3 : la commu ---
with tab_media:
    st.header("Espace Communauté")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📺 Live")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    with col2:
        st.subheader("🔗 Liens")
        st.link_button("Tiktok", "https://www.tiktok.com/@lapoulefolle007?is_from_webapp=1&sender_device=pc")
        st.info("Ton annonce ici ! Contacte Arsène.")