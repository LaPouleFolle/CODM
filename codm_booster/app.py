import streamlit as st
import random
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import plotly.graph_objects as go

# ----------------------
# 1. CONFIGURATION & STYLE (NOIR & JAUNE)
# ----------------------
st.set_page_config(page_title="CODM Booster Pro", layout="centered")

st.markdown("""
    <style>
        /* Fond principal noir */
        .stApp {
            background-color: #0d1117;
            color: #ffffff;
        }
        /* Titres en jaune */
        h1, h2, h3, p {
            color: #facc15 !important;
        }
        /* Style des onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #1e293b;
            border-radius: 4px 4px 0px 0px;
            color: white;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #facc15 !important;
            color: black !important;
        }
        /* Bouton Jaune */
        .stButton>button {
            background-color: #facc15;
            color: black;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------
# 2. BASE DE DONNÉES
# ----------------------
def init_db():
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS performances 
                 (pseudo TEXT, kd REAL, winrate INTEGER, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# (On garde tes fonctions analyser_performance, recommander_build et strategie_par_map ici...)
def analyser_performance(kd_ratio, win_rate):
    if kd_ratio >= 3: niveau = "🔥 Légendaire (tu triches ou quoi ?)"
    elif kd_ratio >= 2: niveau = "🥇 Très bon joueur"
    elif kd_ratio >= 1: niveau = "🥉 Niveau correct (un peu guezz)"
    else: niveau = "🛠 Besoin d'entraînement"
    
    conseils = []
    if win_rate < 50: conseils.append("Travaille ta com' d'équipe frère.")
    if kd_ratio < 1: conseils.append("Change de sensibilité ou d'arme.")
    return niveau, conseils

# ----------------------
# 3. INTERFACE PAR ONGLETS
# ----------------------
st.title("🪖 CODM BOOSTER PRO")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE DU SKILL", "🔫 ARMURERIE & MAPS", "🏆 LEADERBOARD"])

with tab1:
    st.header("Ton Profil")
    with st.form("stats_form"):
        col1, col2 = st.columns(2)
        with col1:
            pseudo = st.text_input("Pseudo")
            kd_ratio = st.number_input("K/D Ratio", min_value=0.0, step=0.1)
        with col2:
            win_rate = st.slider("Win Rate %", 0, 100, 50)
            
        st.write("---")
        reflexes = st.slider("Réflexes", 1, 10, 5)
        strategy = st.slider("Stratégie", 1, 10, 5)
        mobility = st.slider("Mobilité", 1, 10, 5)
        
        submit = st.form_submit_button("LANCER L'ANALYSE")

    if submit:
        # Sauvegarde SQLite
        conn = sqlite3.connect("codm_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO performances VALUES (?, ?, ?, ?)", (pseudo, kd_ratio, win_rate, str(datetime.date.today())))
        conn.commit()
        conn.close()

        # Résultats
        niveau, conseils = analyser_performance(kd_ratio, win_rate)
        st.subheader(f"Résultat : {niveau}")
        for c in conseils:
            st.warning(c)

        # Radar Chart
        categories = ['Réflexes', 'Stratégie', 'Mobilité']
        values = [reflexes, strategy, mobility]
        radar = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line=dict(color='#facc15')))
        radar.update_layout(polar=dict(bgcolor="#1e1e1e"), paper_bgcolor="#0d1117", font_color="#facc15")
        st.plotly_chart(radar)

with tab2:
    st.header("Tactiques & Équipements")
    arme = st.selectbox("Choisis ton arme", ["DL Q33", "RPD", "AK117", "Fennec", "Kilo 141"])
    # Appelle ici ta fonction recommander_build(arme)
    st.info(f"Build conseillé : [Ton code de build ici]")
    
    st.write("---")
    map_name = st.selectbox("Carte", ["Nuketown", "Firing Range", "Summit"])
    # Appelle ici ta fonction strategie_par_map("Multijoueur", map_name)
    st.success(f"Stratégie : [Ton code de strat ici]")

with tab3:
    st.header("Classement Global")
    conn = sqlite3.connect("codm_data.db")
    df = pd.read_sql_query("SELECT pseudo, MAX(kd) as Meilleur_KD, winrate FROM performances GROUP BY pseudo ORDER BY kd DESC", conn)
    conn.close()
    
    if not df.empty:
        st.table(df)
        # Petit bonus : moyenne du serveur
        avg_kd = df['Meilleur_KD'].mean()
        st.metric("Moyenne K/D du serveur", f"{avg_kd:.2f}")
    else:
        st.write("Aucune donnée pour le moment.")
