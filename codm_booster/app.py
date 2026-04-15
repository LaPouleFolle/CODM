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
tab_home, tab_arena, tab_rank, tab_media = st.tabs(["ACCUEIL", "ARENA", "CLASSEMENT", "COMMUNAUTÉ"])
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
        # 1. RÉCUPÉRATION DES LOBBYS ACTIFS
        df_ev = pd.read_sql_query("SELECT id, titre, type FROM evenements", conn)
        
        if df_ev.empty:
            st.warning("⚠️ Aucun lobby n'est ouvert pour le moment. Créez-en un !")
        else:
            # On crée un dictionnaire pour afficher des noms clairs dans la liste déroulante
            liste_lobby = {row['id']: f"[{row['type'].upper()}] {row['titre']}" for _, row in df_ev.iterrows()}
            
            with st.form("form_join_complet"):
                st.subheader("Fiche d'enrôlement")
                
                selected_id = st.selectbox(
                    "Sélectionne ton Match", 
                    options=list(liste_lobby.keys()), 
                    format_func=lambda x: liste_lobby[x]
                )
                
                pseudo = st.text_input("Ton Pseudo", placeholder="Ex: SK_DEMON")
                
                # Le nom de team est libre, mais on va le mettre en majuscule pour éviter les doublons
                team_input = st.text_input("Nom de ton Équipe", placeholder="Ex: Serial Killer, Licteur, le reste vv...")
                
                submit = st.form_submit_button("VALIDER L'INSCRIPTION")
                
                if submit:
                    if pseudo and team_input:
                        # Nettoyage du nom de team (tout en majuscules pour la cohérence)
                        team_name = team_input.strip().upper()
                        
                        # --- DÉBUT DE LA VÉRIFICATION DES LIMITES ---
                        # On récupère les inscrits actuels pour ce lobby précis
                        df_check = pd.read_sql_query(
                            "SELECT pseudo, team_name FROM inscriptions WHERE event_id = ?", 
                            conn, params=(int(selected_id),)
                        )
                        
                        # On récupère le type de l'événement sélectionné
                        current_type = df_ev[df_ev['id'] == selected_id]['type'].values[0]
                        
                        autorise = False
                        msg_erreur = ""

                        # --- LOGIQUE : SCRIM (2 teams max, 6 joueurs max par team) ---
                        if current_type == "Scrim":
                            teams_actuelles = df_check['team_name'].unique()
                            joueurs_ma_team = len(df_check[df_check['team_name'] == team_name])
                            
                            if len(teams_actuelles) >= 2 and team_name not in teams_actuelles:
                                msg_erreur = "Lobby Scrim complet (Déjà 2 équipes inscrites)."
                            elif joueurs_ma_team >= 6:
                                msg_erreur = f"La {team_name} est complète (Max 6 joueurs avec remplaçant)."
                            else:
                                autorise = True

                        # --- LOGIQUE : TOURNOI (20 teams max, 8 joueurs max par team) ---
                        elif current_type == "Tournoi":
                            teams_actuelles = df_check['team_name'].unique()
                            joueurs_ma_team = len(df_check[df_check['team_name'] == team_name])
                            
                            if len(teams_actuelles) >= 20 and team_name not in teams_actuelles:
                                msg_erreur = "Tournoi complet (Limite de 20 équipes atteinte)."
                            elif joueurs_ma_team >= 8:
                                msg_erreur = f"L'équipe {team_name} est complète (Max 8 joueurs)."
                            else:
                                autorise = True

                        # --- LOGIQUE : RANKED (5 joueurs max au total) ---
                        elif current_type == "Ranked":
                            if len(df_check) >= 5:
                                msg_erreur = "Squad Ranked complète (Max 5 joueurs)."
                            else:
                                autorise = True

                        # --- ACTION FINALE ---
                        if autorise:
                            # On vérifie si le pseudo n'est pas déjà inscrit dans ce lobby
                            if pseudo.lower() in [p.lower() for p in df_check['pseudo'].tolist()]:
                                st.error(f"🛑 Soldat {pseudo}, tu es déjà sur la liste !")
                            else:
                                conn.execute(
                                    "INSERT INTO inscriptions (event_id, pseudo, team_name) VALUES (?,?,?)", 
                                    (int(selected_id), pseudo, team_name)
                                )
                                conn.commit()
                                st.success(f"✅ Déploiement confirmé : {pseudo} rejoint la {team_name} !")
                                st.rerun()
                        else:
                            st.error(f"❌ Accès refusé : {msg_erreur}")
                    else:
                        st.warning("⚠️ Soldat, remplis ton pseudo et le nom de ton équipe !")

    # SECTION : SUIVI & TEAMS (AUTOMATIQUE)

    elif choix == "📊 Suivi & Teams":
        df_ev = pd.read_sql_query("SELECT * FROM evenements", conn)
        
        if df_ev.empty:
            st.info("Aucune donnée disponible.")
        else:
            for _, ev in df_ev.iloc[::-1].iterrows():
                with st.expander(f"📋 {ev['type']} : {ev['titre']}"):
                    st.write(f"📍 Maps: {ev['maps']} | 🎮 Modes: {ev['modes']}")
                    
                    df_p = pd.read_sql_query("SELECT pseudo, team_name FROM inscriptions WHERE event_id = ?", conn, params=(ev['id'],))
                    
                    if df_p.empty:
                        st.write("Aucun joueur inscrit pour le moment.")
                    else:
                        teams = df_p['team_name'].unique()
                        cols = st.columns(len(teams) if len(teams) > 0 else 1)
                        
                        for i, t_name in enumerate(teams):
                            with cols[i % len(cols)]:
                                pseudos_team = df_p[df_p['team_name'] == t_name]['pseudo'].tolist()
                                st.markdown(f"""
                                <div class='team-card'>
                                    <h3 style='color:#FF4D00 !important;'>{t_name.upper()}</h3>
                                    <p>{'<br>'.join(pseudos_team)}</p>
                                    <small>{len(pseudos_team)} joueurs</small>
                                </div>
                                """, unsafe_allow_html=True)

                        # --- LE DASHBOARD DE MATCH ---
                        st.divider()
                        
                        # SÉCURITÉ : On vérifie qu'il y a bien 2 équipes avant d'afficher le score
                        if len(teams) < 2:
                            st.warning("⏳ En attente d'une équipe adverse pour activer le score...")
                        else:
                            st.subheader("🕹️ SCORE LIVE (BO3 - Premier à 2 victoires)")

                            sc_col1, sc_col2 = st.columns(2)
                            # On affiche les scores seulement si on a bien teams[0] et teams[1]
                            s1 = sc_col1.number_input(f"Manches {teams[0]}", min_value=0, max_value=2, key=f"s1_{ev['id']}")
                            s2 = sc_col2.number_input(f"Manches {teams[1]}", min_value=0, max_value=2, key=f"s2_{ev['id']}")

                            # Empêcher l'égalité 2-2 en BO3
                            if s1 == 2 and s2 == 2:
                                st.error("Impossible : En BO3, il ne peut pas y avoir 2-2 !")
                            else:
                                mvp = st.selectbox("Sélectionner le MVP du match", ["---"] + list(df_p['pseudo']), key=f"mvp_{ev['id']}")
                                
                                # Le bouton n'apparaît que si une équipe a gagné (score de 2)
                                if (s1 == 2 or s2 == 2) and mvp != "---":
                                    if st.button("🏆 ENREGISTRER LE RÉSULTAT FINAL", key=f"fin_{ev['id']}"):
                                        gagnant = teams[0] if s1 > s2 else teams[1]
                                        
                                        # Mise à jour du titre pour marquer comme fini
                                        conn.execute("UPDATE evenements SET titre = ? WHERE id = ?", (f"✅ FINI: {ev['titre']}", ev['id']))
                                        
                                        # Distribution des points
                                        for _, row_p in df_p.iterrows():
                                            p_pts = 10 if row_p['pseudo'] == mvp else (5 if row_p['team_name'] == gagnant else 0)
                                            conn.execute("UPDATE inscriptions SET score = score + ? WHERE pseudo = ? AND event_id = ?", 
                                                         (p_pts, row_p['pseudo'], ev['id']))
                                        
                                        conn.commit()
                                        st.balloons()
                                        st.success(f"Victoire de {gagnant} ! MVP: {mvp}")
                                        st.rerun()           
                        
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
    
    st.info("Disponible pour des projets en Python/SQL.")

# --- ONGLET : CLASSEMENT ---
with tab_rank:
    st.header("Hall of Fame - TOP 10")
    # On récupère le score total de chaque joueur sur tous les matchs
    df_leaderboard = pd.read_sql_query("""
        SELECT pseudo, SUM(score) as Total_Points 
        FROM inscriptions 
        GROUP BY pseudo 
        ORDER BY Total_Points DESC 
        LIMIT 10
    """, conn)

    if df_leaderboard.empty:
        st.info("Le classement sera disponible après les premiers matchs terminés.")
    else:
        for index, row in df_leaderboard.iterrows():
            # Design pour le podium
            color = "#FFD700" if index == 0 else ("#C0C0C0" if index == 1 else "#CD7F32")
            if index > 2: color = "#FFFFFF"
            
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; 
                     background: #1A1A1A; padding: 10px 20px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 5px;'>
                    <span style='font-size: 1.2em; font-weight: bold;'>#{index+1} {row['pseudo']}</span>
                    <span style='color: #FF4D00; font-weight: bold;'>{row['Total_Points']} PTS</span>
                </div>
            """, unsafe_allow_html=True)

conn.close()