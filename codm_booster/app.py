import streamlit as st
import sqlite3
import pandas as pd
import random
import datetime
import os

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Appplication CODM", layout="wide")

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

# 3. LOGIQUE BASE DE DONNÉES 
def get_db_connection():
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    # Table des lobby
    conn.execute('''CREATE TABLE IF NOT EXISTS evenements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, leader TEXT, titre TEXT, maps TEXT, modes TEXT)''')
    # Table des joueurs (avec team_name saisi par l'user)
    conn.execute('''CREATE TABLE IF NOT EXISTS inscriptions 
                 (event_id INTEGER, pseudo TEXT, team_name TEXT)''')
    conn.commit()
    return conn

# Initialisation
conn = get_db_connection()

# 4. titre de page
st.markdown("<h1 style='text-align: center; font-size: 3.5em;'>🎮 CODM - ORGANISATION</h1>", unsafe_allow_html=True)

# 5. NAVIGATION PAR ONGLETS (On garde tes 3 onglets !)
tab_home, tab_arena, tab_media = st.tabs([" ACCUEIL", " ARENA (DRAFT 10J)", " COMMUNAUTÉ & CONTACT"])

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
        type_event = st.selectbox("Type d'événement", ["Scrim", "Tournoi", "Ranked"])
        
        with st.form("form_create"):
            leader = st.text_input("Pseudo du Chef")
            titre = st.text_input("Nom de l'Opération")
            
            if type_event == "Scrim":
                maps = st.multiselect("Maps (Choisissez 3)", ["Nuketown", "Firing Range", "Summit", "Standoff", "Raid"], max_selections=3)
                modes = st.multiselect("Modes", ["HP", "SND", "CONTROLE"])
            elif type_event == "Tournoi":
                maps = st.multiselect("Maps du Tournoi", ["Nuketown", "Firing Range", "Summit", "Standoff", "Raid"])
                modes = st.multiselect("Modes du Tournoi", ["HP", "SND", "CONTROLE"])
            else:
                maps, modes = "Rotation Ranked", "Tous les modes"

            if st.form_submit_button("OUVRIR LE LOBBY"):
                if leader and titre:
                    m_str = ", ".join(maps) if isinstance(maps, list) else maps
                    mo_str = ", ".join(modes) if isinstance(modes, list) else modes
                    conn.execute("INSERT INTO evenements (type, leader, titre, maps, modes, date) VALUES (?,?,?,?,?,?)", 
                                 (type_event, leader, titre, m_str, mo_str, str(datetime.date.today())))
                    conn.commit()
                    st.success(f"{type_event} ouvert !")

    # SECTION : INSCRIPTION
    elif choix == "📝 Rejoindre":
        # 1. On récupère la liste des lobby existants
        df_ev = pd.read_sql_query("SELECT id, titre, type FROM evenements", conn)
        
        if df_ev.empty:
            st.warning("⚠️ Aucun lobby n'est ouvert pour le moment. Créez-en un !")
        else:
            # Création d'une liste propre pour le menu déroulant
            liste_lobby = {row['id']: f"[{row['type']}] {row['titre']}" for _, row in df_ev.iterrows()}
            
            with st.form("form_join"):
                selected_id = st.selectbox("Sélectionne ton Match", options=list(liste_lobby.keys()), format_func=lambda x: liste_lobby[x])
                pseudo = st.text_input("Ton Pseudo IG")
                
                # Nom de team dynamique : l'utilisateur écrit ce qu'il veut
                team_name = st.text_input("Nom de ton Équipe (ex: Team Demon, Alpha, Squad 7...)")
                
                submit = st.form_submit_button("REJOINDRE LE COMBAT")
                
                if submit:
                    if pseudo and team_name:
                        conn.execute("INSERT INTO inscriptions (event_id, pseudo, team_name) VALUES (?,?,?)", 
                                     (int(selected_id), pseudo, team_name))
                        conn.commit()
                        st.success(f"Soldat {pseudo} a rejoint la {team_name} !")
                        st.rerun() # Rafraîchit pour voir la liste direct
                    else:
                        st.error("Pseudo et Nom d'équipe obligatoires !")

    # SECTION : SUIVI & TEAMS (AUTOMATIQUE)
    elif choix == "📊 Suivi & Teams":
        df_ev = pd.read_sql_query("SELECT * FROM evenements", conn)
        
        if df_ev.empty:
            st.info("Aucune donnée disponible.")
        else:
            for _, ev in df_ev.iloc[::-1].iterrows():
                with st.expander(f"📋 {ev['type']} : {ev['titre']}"):
                    st.write(f"📍 Maps: {ev['maps']} | 🎮 Modes: {ev['modes']}")
                    
                    # On récupère les joueurs de ce lobby
                    df_p = pd.read_sql_query("SELECT pseudo, team_name FROM inscriptions WHERE event_id = ?", conn, params=(ev['id'],))
                    
                    if df_p.empty:
                        st.write("Aucun joueur inscrit pour le moment.")
                    else:
                        # On regroupe les joueurs par le nom de team qu'ils ont saisi
                        teams = df_p['team_name'].unique()
                        cols = st.columns(len(teams) if len(teams) > 0 else 1)
                        
                        for i, t_name in enumerate(teams):
                            with cols[i % len(cols)]:
                                # Liste des pseudos pour cette team précise
                                pseudos_team = df_p[df_p['team_name'] == t_name]['pseudo'].tolist()
                                st.markdown(f"""
                                <div class='team-card'>
                                    <h3 style='color:#FF4D00 !important;'>{t_name.upper()}</h3>
                                    <p>{'<br>'.join(pseudos_team)}</p>
                                    <small>{len(pseudos_team)} joueurs</small>
                                </div>
                                """, unsafe_allow_html=True)
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
    
    st.info("🚀 Disponible pour des projets en Python/SQL.")

conn.close()