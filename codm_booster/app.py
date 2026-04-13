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
    # ma table de stat existante (à voir si je la garde)
    c.execute('''CREATE TABLE IF NOT EXISTS performances 
                 (pseudo TEXT, kd REAL, date TEXT)''') # winrate supprimé ici
    
    # Nouvelle table pour enregistré les scrims (Tournois/Scrims)
    c.execute('''CREATE TABLE IF NOT EXISTS evenements 
                 (organisateur TEXT, type TEXT, date_evenement TEXT, details TEXT)''')
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
tab_home, tab_compete, tab_media = st.tabs(["Accueil", "Analyse & Stats", "📺 Communauté & Live"])

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

    st.subheader("🏆 Top Global Gabon")
    conn = sqlite3.connect("codm_data.db")
    df_top = pd.read_sql_query("SELECT pseudo, MAX(kd) as kd FROM performances GROUP BY pseudo ORDER BY kd DESC LIMIT 5", conn)
    st.table(df_top)
    conn.close()
    
# --- Onglet 2 : analyse 
with tab_compete:
    st.header("🏆 Big Match")
    
    # Menu de navigation interne
    sub_menu = st.radio(
        "Navigation", 
        ["📊 Mon Analyse", "🔥 Scrims & Tournois", "📋 Suivi des Inscriptions"], 
        horizontal=True
    )

    st.divider()

    # --- SECTION 1 : ANALYSE (Gardée simple) ---
    if sub_menu == "📊 Mon Analyse":
        col_form, col_info = st.columns([1, 1])
        with col_form:
            with st.form("stats_form"):
                pseudo_stat = st.text_input("Pseudo IG")
                kd_stat = st.number_input("K/D Ratio", min_value=0.0, step=0.01)
                win_stat = st.slider("Win Rate (%)", 0, 100, 50)
                if st.form_submit_button("ENREGISTRER MES PERFS"):
                    if pseudo_stat:
                        sauvegarder_stats_sql(pseudo_stat, kd_stat, win_stat)
                        st.success(f"Stats de {pseudo_stat} mises à jour !")
        with col_info:
            st.info("💡 Enregistre tes stats régulièrement pour apparaître dans le Top Global de l'accueil.")

    # --- SECTION 2 : CRÉATION DE SCRIMS & TOURNOIS ---
    elif sub_menu == "🔥 Scrims & Tournois":
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            st.subheader("📢 Créer une annonce")
            with st.form("event_form"):
                org = st.text_input("Organisateur / Clan")
                type_ev = st.selectbox("Type", ["SCRIM (Amical)", "TOURNOI (Cashprize)", "RANKED PUSH"])
                titre = st.text_input("Nom de l'opération")
                cash = st.text_input("Récompense")
                desc = st.text_area("Détails")
                if st.form_submit_button("PUBLIER"):
                    conn = sqlite3.connect("codm_data.db")
                    conn.execute("INSERT INTO evenements (organisateur, type, titre, date, details, cashprize) VALUES (?,?,?,?,?,?)",
                                 (org, type_ev, titre, str(datetime.date.today()), desc, cash))
                    conn.commit()
                    conn.close()
                    st.success("Annonce publiée !")

        with c2:
            st.subheader("📅 Matchs Disponibles")
            conn = sqlite3.connect("codm_data.db")
            # On s'assure que la table existe
            conn.execute("CREATE TABLE IF NOT EXISTS evenements (id INTEGER PRIMARY KEY AUTOINCREMENT, organisateur TEXT, type TEXT, titre TEXT, date TEXT, details TEXT, cashprize TEXT)")
            df_ev = pd.read_sql_query("SELECT * FROM evenements", conn)
            conn.close()

            if not df_ev.empty:
                for i, row in df_ev.iloc[::-1].iterrows():
                    st.markdown(f"""
                        <div style="background-color: #1A1A1A; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4D00; margin-bottom: 10px;">
                            <h3 style="margin:0; color:#FF4D00 !important;">{row['titre']}</h3>
                            <p style="margin:2px 0; font-size:0.9em;">{row['type']} | Par {row['organisateur']}</p>
                            <p style="color:#BBB; font-size:0.8em;">{row['details']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # FORMULAIRE D'INSCRIPTION
                    with st.expander(f"S'inscrire à {row['titre']}"):
                        with st.form(key=f"insc_{row['id']}"):
                            p_name = st.text_input("Ton Pseudo / Team")
                            p_cont = st.text_input("Contact (WhatsApp/Discord)")
                            if st.form_submit_button("VALIDER"):
                                conn = sqlite3.connect("codm_data.db")
                                # Création table inscription si absente
                                conn.execute("CREATE TABLE IF NOT EXISTS inscriptions (event_id INTEGER, participant TEXT, contact TEXT)")
                                conn.execute("INSERT INTO inscriptions (event_id, participant, contact) VALUES (?,?,?)",
                                             (row['id'], p_name, p_cont))
                                conn.commit()
                                conn.close()
                                st.success("Inscription enregistrée ! Check l'onglet Suivi.")

    # --- SECTION 3 : SUIVI DES INSCRIPTIONS (REMPlACE ADMIN) ---
    elif sub_menu == "📋 Suivi des Inscriptions":
        st.subheader("👀 Qui participe à quoi ?")
        
        conn = sqlite3.connect("codm_data.db")
        # On vérifie si les tables existent pour éviter les crashs
        check_insc = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inscriptions'").fetchone()
        
        if check_insc:
            # On fait une jointure SQL pour lier le nom du tournoi au participant
            query = """
                SELECT evenements.titre as 'Tournoi/Scrim', inscriptions.participant as 'Joueur/Team', inscriptions.contact as 'Contact'
                FROM inscriptions
                JOIN evenements ON evenements.id = inscriptions.event_id
            """
            df_suivi = pd.read_sql_query(query, conn)
            conn.close()

            if not df_suivi.empty:
                st.dataframe(df_suivi, use_container_width=True)
                st.info("ℹ️ Les organisateurs peuvent utiliser ces contacts pour créer les groupes de match.")
            else:
                st.write("Aucune inscription enregistrée pour le moment.")
        else:
            conn.close()
            st.write("La zone est calme... Trop calme. Personne n'est encore inscrit.")

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
        st.video("https://youtu.be/8Oyl2sQE7JI?si=SgEaZcJwlHroRSRJ")
    with col2:
        st.subheader("🔗 Liens")
        st.link_button("Tiktok", "https://www.tiktok.com/@lapoulefolle007?is_from_webapp=1&sender_device=pc")
        st.info("Pour tout besoin de spec sur les lives , me contacter")

    st.divider()
    
    # Tout ce qui suit doit être aligné ici pour rester dans l'onglet
    st.subheader("Contact & Collaborations")

    # Création de 3 colonnes
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### Email")
        st.write("arsenemeye.mb@gmail.com")

    with c2:
        st.markdown("### Téléphone")
        st.write("+33 7 66 88 61 72")

    with c3:
        st.markdown("### 🔗 LinkedIn")
        st.link_button("Voir mon profil", "www.linkedin.com/in/arsène-mbabeh-meye-4823a9258")

    # Petit bandeau de fin (aligné avec c1, c2, c3)
    st.info("Disponible pour du coaching CODM ou des projets de développement Python ou Base de donnée SQL.")