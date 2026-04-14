import streamlit as st
import sqlite3
import pandas as pd
import random
import datetime
import os

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="CODM ARENA PRO", layout="wide")

# 2. DESIGN & STYLE (Orange & Noir + Effets GFX)
st.markdown("""
    <style>
        .stApp { background-color: #0A0A0A; }
        h1, h2, h3, label { color: #FF4D00 !important; font-family: 'Arial Black', sans-serif; }
        .stMarkdown, p, span { color: #FFFFFF !important; }
        
        /* Boutons personnalisés */
        .stButton>button {
            background: linear-gradient(90deg, #FF4D00 0%, #CC3D00 100%);
            color: white; border-radius: 8px; font-weight: bold; border: none; height: 3em; width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0px 0px 20px rgba(255, 77, 0, 0.5);
            transform: scale(1.02);
        }

        /* Cartes d'équipes */
        .team-card {
            background-color: #161616;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #FF4D00;
            text-align: center;
            margin-bottom: 10px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        }
        
        /* Barre de progression */
        .stProgress > div > div > div > div { background-color: #FF4D00; }

        /* Style des inputs */
        input, textarea, select {
            background-color: #1A1A1A !important;
            color: white !important;
            border: 1px solid #333 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. LOGIQUE BASE DE DONNÉES (Zéro Erreur)
def get_db_connection():
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    # Table des Scrims
    conn.execute('''CREATE TABLE IF NOT EXISTS scrims 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, leader TEXT, titre TEXT, map TEXT, date TEXT)''')
    # Table des Inscriptions (avec contact pour le suivi)
    conn.execute('''CREATE TABLE IF NOT EXISTS inscriptions 
                 (scrim_id INTEGER, pseudo TEXT, contact TEXT)''')
    conn.commit()
    return conn

# Initialisation
conn = get_db_connection()

# 4. TITRE
st.markdown("<h1 style='text-align: center; font-size: 3.5em;'>🎮 CODM ARENA COMMAND</h1>", unsafe_allow_html=True)

# 5. NAVIGATION PAR ONGLETS (On garde tes 3 onglets !)
tab_home, tab_arena, tab_media = st.tabs(["🏠 ACCUEIL", "🏆 ARENA (DRAFT 10J)", "📺 COMMUNAUTÉ & CONTACT"])

# --- ONGLET 1 : ACCUEIL ---
with tab_home:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Briefing de Mission")
        st.write("Bienvenue sur la plateforme **CODM Booster**. Ici, on ne rigole pas avec le skill.")
        st.write("Utilise l'onglet **ARENA** pour lancer des matchs ou rejoindre un lobby de 10 joueurs.")
        st.image("https://i.pinimg.com/originals/05/90/ab/0590abeb7e74f434902def84fef8dff3.jpg", use_container_width=True)
    with col2:
        st.info("💡 Le système de Draft mélange automatiquement les inscrits pour créer des teams équilibrées dès que le quota de 10 joueurs est atteint.")

# --- ONGLET 2 : ARENA (LE SYSTÈME DE DRAFT) ---
with tab_arena:
    choix = st.radio("Actions Tactiques", ["📡 Créer un Lobby", "📝 Rejoindre", "📊 Suivi & Teams"], horizontal=True)
    st.divider()

    # SECTION : CRÉATION
    if choix == "📡 Créer un Lobby":
        with st.form("form_create"):
            leader = st.text_input("Pseudo du Chef de Lobby")
            nom_scrim = st.text_input("Nom de l'Opération (ex: Scrim du Soir)")
            map_name = st.selectbox("Map", ["Nuketown", "Firing Range", "Summit", "Standoff", "Raid"])
            if st.form_submit_button("OUVRIR LE LOBBY"):
                if leader and nom_scrim:
                    conn.execute("INSERT INTO scrims (leader, titre, map, date) VALUES (?,?,?,?)", 
                                 (leader, nom_scrim, map_name, str(datetime.date.today())))
                    conn.commit()
                    st.success(f"Lobby '{nom_scrim}' ouvert !")
                else:
                    st.error("Remplis les champs, soldat.")

    # SECTION : INSCRIPTION
    elif choix == "📝 Rejoindre":
        df_scrims = pd.read_sql_query("SELECT id, titre, leader FROM scrims", conn)
        if df_scrims.empty:
            st.warning("Aucun lobby ouvert pour le moment.")
        else:
            with st.form("form_join"):
                sid = st.selectbox("Choisir un match", df_scrims['id'], 
                                   format_func=lambda x: f"ID {x} - {df_scrims[df_scrims['id']==x]['titre'].values[0]}")
                pseudo = st.text_input("Ton Pseudo IG")
                contact = st.text_input("WhatsApp / Discord (pour le suivi)")
                if st.form_submit_button("REJOINDRE LE MATCH"):
                    if pseudo and contact:
                        # Vérification doublon
                        check = pd.read_sql_query("SELECT * FROM inscriptions WHERE scrim_id = ? AND pseudo = ?", conn, params=(int(sid), pseudo))
                        if check.empty:
                            conn.execute("INSERT INTO inscriptions (scrim_id, pseudo, contact) VALUES (?,?,?)", (int(sid), pseudo, contact))
                            conn.commit()
                            st.success(f"Soldat {pseudo} paré au combat !")
                        else:
                            st.warning("Tu es déjà inscrit !")
                    else:
                        st.error("Pseudo et Contact requis.")

    # SECTION : SUIVI & TEAMS (AUTOMATIQUE)
    elif choix == "📊 Suivi & Teams":
        df_scrims = pd.read_sql_query("SELECT * FROM scrims", conn)
        if df_scrims.empty:
            st.write("La zone est calme. Aucun match en cours.")
        else:
            for _, scrim in df_scrims.iloc[::-1].iterrows():
                st.markdown(f"### 🎯 Match : {scrim['titre']} (Leader: {scrim['leader']})")
                df_players = pd.read_sql_query("SELECT pseudo, contact FROM inscriptions WHERE scrim_id = ?", conn, params=(scrim['id'],))
                count = len(df_players)
                
                if count < 10:
                    st.write(f"👥 Effectif : **{count} / 10**")
                    st.progress(count / 10)
                    st.write("Inscrits : " + ", ".join(df_players['pseudo'].tolist()))
                else:
                    st.success("🔥🔥 QUORUM ATTEINT ! GÉNÉRATION DES TEAMS 🔥🔥")
                    players = df_players['pseudo'].tolist()
                    random.seed(scrim['id']) # Pour garder les mêmes teams au refresh
                    random.shuffle(players)
                    
                    team_a, team_b = players[:5], players[5:10]
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"<div class='team-card'><h3 style='color:#0088FF !important;'>🔵 TEAM ALPHA</h3>{'<br>'.join(team_a)}</div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<div class='team-card'><h3 style='color:#FF4D00 !important;'>🔴 TEAM BRAVO</h3>{'<br>'.join(team_b)}</div>", unsafe_allow_html=True)
                    
                    st.write("**Contacts des joueurs :**")
                    st.dataframe(df_players, use_container_width=True)
                st.divider()

# --- ONGLET 3 : COMMUNAUTÉ & CONTACT (TES INFOS) ---
with tab_media:
    st.header("Espace Communauté")
    col_v, col_l = st.columns(2)
    with col_v:
        st.subheader("📺 Dernier Live / Vidéo")
        st.video("https://youtu.be/8Oyl2sQE7JI?si=SgEaZcJwlHroRSRJ")
    with col_l:
        st.subheader("🔗 Liens Utiles")
        st.link_button("Mon TikTok", "https://www.tiktok.com/@lapoulefolle007")
        st.info("Abonne-toi pour ne rien rater des prochains tournois !")

    st.divider()
    st.subheader("📩 Contact & Collaborations")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Email :** arsenemeye.mb@gmail.com")
    c2.markdown(f"**Téléphone :** +33 7 66 88 61 72")
    c3.link_button("LinkedIn", "https://www.linkedin.com/in/arsène-mbabeh-meye-4823a9258")
    
    st.info("🚀 Disponible pour du coaching CODM ou des projets Python/SQL.")

conn.close()