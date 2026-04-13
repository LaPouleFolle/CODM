import streamlit as st
import datetime
import pandas as pd
import sqlite3
import os
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="CODM BOOSTER PRO", layout="wide")

# --- STYLE CSS (ORANGE & NOIR) ---
st.markdown("""
    <style>
        .stApp { background-color: #0F0F0F; }
        h1, h2, h3, label, p { color: #FF4D00 !important; font-family: 'Segoe UI', sans-serif; }
        .stMarkdown { color: white !important; }
        .stButton>button { 
            background-color: #FF4D00; color: white; border-radius: 5px; 
            font-weight: bold; width: 100%; border: none;
        }
        .stButton>button:hover { background-color: #CC3D00; box-shadow: 0px 0px 10px #FF4D00; }
        .stTabs [data-baseweb="tab-list"] { background-color: #1A1A1A; }
        .stTabs [data-baseweb="tab"] { color: #888; }
        .stTabs [aria-selected="true"] { color: #FF4D00 !important; border-bottom-color: #FF4D00 !important; }
        div[data-testid="stMetricValue"] { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES (ARCHITECTURE AVANCÉE) ---
def init_db():
    conn = sqlite3.connect("codm_data.db", check_same_thread=False)
    c = conn.cursor()
    # Table Performances
    c.execute('CREATE TABLE IF NOT EXISTS performances (pseudo TEXT, kd REAL, date TEXT)')
    # Table Événements (Scrims/Tournois)
    c.execute('''CREATE TABLE IF NOT EXISTS evenements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, organisateur TEXT, type TEXT, 
                  titre TEXT, date TEXT, details TEXT, cashprize TEXT, status TEXT)''')
    # Table Inscriptions (Lien entre Joueurs et Événements)
    c.execute('''CREATE TABLE IF NOT EXISTS inscriptions 
                 (event_id INTEGER, participant TEXT, equipe TEXT, contact TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- FONCTIONS UTILES ---
def get_db_connection():
    return sqlite3.connect("codm_data.db", check_same_thread=False)

# --- INTERFACE PRINCIPALE ---
st.title("🎮 CODM ARENA : COMMAND CENTER")

tab_home, tab_compete, tab_media = st.tabs(["🏠 ACCUEIL", "🏆 COMPÉTITION & SCRIMS", "📺 COMMUNAUTÉ"])

# --- ONGLET 1 : ACCUEIL ---
with tab_home:
    st.markdown("<h2 style='text-align: center;'>VOS STATISTIQUES GLOBALES</h2>", unsafe_allow_html=True)
    conn = get_db_connection()
    df_stats = pd.read_sql_query("SELECT kd FROM performances", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Soldats Identifiés", len(df_stats))
    with col2: 
        val = df_stats['kd'].mean() if not df_stats.empty else 0
        st.metric("K/D Moyen Communauté", f"{val:.2f}")
    with col3: st.metric("Serveur Status", "OPÉRATIONNEL ✅")

    st.divider()
    st.subheader("🏆 CLASSEMENT TOP GABON")
    df_top = pd.read_sql_query("SELECT pseudo, MAX(kd) as kd FROM performances GROUP BY pseudo ORDER BY kd DESC LIMIT 5", conn)
    st.dataframe(df_top, use_container_width=True)
    conn.close()

# --- ONGLET 2 : COMPÉTITION & ORGANISATION (LE GROS MORCEAU) ---
with tab_compete:
    st.header("🏆 GESTION DES OPÉRATIONS")
    
    # --- SUB-NAVIGATION ---
    choice = st.radio("Menu", ["Explorer les Matchs", "Organiser un Événement", "Administration"], horizontal=True)

    if choice == "Organiser un Événement":
        with st.form("create_event"):
            st.subheader("➕ CRÉER UNE NOUVELLE OPÉRATION")
            col_a, col_b = st.columns(2)
            with col_a:
                pseudo_org = st.text_input("Pseudo Organisateur / Leader Team")
                type_ev = st.selectbox("Type", ["TOURNOI", "SCRIM AMICAL", "RANKED PARTY", "RECRUTEMENT"])
                titre = st.text_input("Nom de l'opération")
            with col_b:
                date_ev = st.date_input("Date")
                cash = st.text_input("Récompense (ex: Gloire, 10€, 5000 CP)")
                status = "OUVERT"
            
            details = st.text_area("Règles, Maps et Configuration")
            submit = st.form_submit_button("PUBLIER SUR L'ARENA")
            
            if submit:
                if pseudo_org and titre:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO evenements (organisateur, type, titre, date, details, cashprize, status) VALUES (?,?,?,?,?,?,?)",
                                 (pseudo_org, type_ev, titre, str(date_ev), details, cash, status))
                    conn.commit()
                    conn.close()
                    st.success("✅ Opération publiée avec succès !")
                else:
                    st.error("❌ Erreur : Pseudo et Titre obligatoires.")

    elif choice == "Explorer les Matchs":
        conn = get_db_connection()
        df_ev = pd.read_sql_query("SELECT * FROM evenements WHERE status = 'OUVERT'", conn)
        
        if df_ev.empty:
            st.info("Aucune opération en cours. Lancez la vôtre !")
        else:
            for i, row in df_ev.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                        <div style="background: #1A1A1A; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4D00; margin-bottom: 20px;">
                            <h3 style="margin:0;">{row['titre']} <span style="font-size:0.6em; color:#888;">({row['type']})</span></h3>
                            <p style="color:#FF4D00;">📅 {row['date']} | 💰 {row['cashprize']}</p>
                            <p style="color:#DDD;">{row['details']}</p>
                            <p style="font-size:0.8em; color:#555;">Organisé par : {row['organisateur']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Formulaire d'inscription rapide
                    with st.expander(f"📥 Rejoindre / S'inscrire à {row['titre']}"):
                        with st.form(key=f"join_{row['id']}"):
                            player = st.text_input("Pseudo du joueur / Nom de la Team")
                            contact = st.text_input("Contact (Discord/WhatsApp)")
                            if st.form_submit_button("VALIDER L'INSCRIPTION"):
                                conn.execute("INSERT INTO inscriptions (event_id, participant, contact) VALUES (?,?,?)",
                                             (row['id'], player, contact))
                                conn.commit()
                                st.success(f"Soldat {player} enregistré !")
        conn.close()

    elif choice == "Administration":
        st.subheader("⚙️ GESTION ADMINISTRATIVE")
        pwd = st.text_input("Code Admin", type="password")
        if pwd == "DEMON": # Ton code secret
            conn = get_db_connection()
            st.write("### Liste des inscrits par événement")
            df_inscr = pd.read_sql_query("""
                SELECT evenements.titre, inscriptions.participant, inscriptions.contact 
                FROM inscriptions 
                JOIN evenements ON evenements.id = inscriptions.event_id
            """, conn)
            st.table(df_inscr)
            
            if st.button("🔴 RÉINITIALISER TOUTES LES DONNÉES"):
                conn.execute("DELETE FROM evenements")
                conn.execute("DELETE FROM inscriptions")
                conn.commit()
                st.warning("Zone nettoyée.")
            conn.close()

# --- ONGLET 3 : COMMUNAUTÉ ---
with tab_media:
    st.header("📺 QUARTIER GÉNÉRAL")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📺 DERNIER BRIEFING (LIVE)")
        st.video("https://youtu.be/8Oyl2sQE7JI?si=SgEaZcJwlHroRSRJ")
    with col2:
        st.subheader("🔗 RÉSEAUX SOCIAUX")
        st.link_button("TIKTOK OFFICIEL", "https://www.tiktok.com/@lapoulefolle007")
        st.info("Contactez l'admin pour devenir spectateur officiel.")

    st.divider()
    st.subheader("📩 CONTACT DIRECT")
    c1, c2, c3 = st.columns(3)
    c1.markdown("📧 **Email** : arsenemeye.mb@gmail.com")
    c2.markdown("📱 **WhatsApp** : +33 7 66 88 61 72")
    c3.link_button("LINKEDIN", "https://www.linkedin.com/in/arsène-mbabeh-meye-4823a9258")

    st.info("🚀 Développé par SK DEMON - Expert Python & SQL")