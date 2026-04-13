import streamlit as st
import datetime
import pandas as pd
import sqlite3
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CODM ARENA PRO", 
    page_icon="🎮", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. STYLE CSS PERSONNALISÉ (DÉMON MODE) ---
st.markdown("""
    <style>
        .stApp { background-color: #0A0A0A; }
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        
        /* Titres et Textes */
        h1, h2, h3 { color: #FF4D00 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
        .stMarkdown, p, span { color: #E0E0E0 !important; }
        
        /* Cartes d'événements */
        .event-card {
            background: #161616;
            padding: 20px;
            border-radius: 15px;
            border-left: 6px solid #FF4D00;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        
        /* Inputs et Formulaires */
        .stTextInput>div>div>input, .stSelectbox>div>div, .stTextArea>div>div>textarea {
            background-color: #1A1A1A !important;
            color: white !important;
            border: 1px solid #333 !important;
        }
        
        /* Boutons */
        .stButton>button {
            background: linear-gradient(90deg, #FF4D00 0%, #CC3D00 100%);
            color: white; border: none; font-weight: bold;
            padding: 10px 20px; border-radius: 8px; width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0 0 20px rgba(255, 77, 0, 0.4);
            transform: translateY(-2px);
            color: white;
        }
        
        /* Métriques */
        [data-testid="stMetricValue"] { color: #FF4D00 !important; font-size: 2em !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE BASE DE DONNÉES (SQL) ---
def get_connection():
    return sqlite3.connect("codm_data.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Table Performances (Stats)
    c.execute('''CREATE TABLE IF NOT EXISTS performances 
                 (pseudo TEXT, kd REAL, date TEXT)''')
    # Table Événements (Tournois/Scrims)
    c.execute('''CREATE TABLE IF NOT EXISTS evenements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, organisateur TEXT, type TEXT, 
                  titre TEXT, date TEXT, details TEXT, cashprize TEXT, status TEXT)''')
    # Table Inscriptions
    c.execute('''CREATE TABLE IF NOT EXISTS inscriptions 
                 (event_id INTEGER, participant TEXT, contact TEXT, date_insc TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 4. BARRE LATÉRALE (INFOS) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/1/17/Call_of_Duty_Mobile_logo.png", width=150)
    st.title("Admin Panel")
    access_code = st.text_input("Code Secret", type="password")
    if access_code == "DEMON":
        st.success("Accès Autorisé")
        if st.button("Vider la base de données"):
            conn = get_connection()
            conn.execute("DELETE FROM evenements")
            conn.execute("DELETE FROM inscriptions")
            conn.commit()
            conn.close()
            st.rerun()

# --- 5. EN-TÊTE PRINCIPAL ---
st.markdown("<h1 style='text-align: center; font-size: 3.5em;'>CODM ARENA COMMAND</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Plateforme de gestion de compétition - Développé par SK DEMON</p>", unsafe_allow_html=True)

tab_home, tab_compete, tab_analyse, tab_contact = st.tabs([
    "🏠 QUARTIER GÉNÉRAL", "🏆 ARENA DE COMBAT", "📊 ANALYSE STATS", "📩 CONTACT & LIVES"
])

# --- 6. ONGLET : ACCUEIL ---
with tab_home:
    conn = get_connection()
    df_count = pd.read_sql_query("SELECT COUNT(*) as total FROM performances", conn)
    df_events = pd.read_sql_query("SELECT COUNT(*) as total FROM evenements", conn)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Soldats Recensés", df_count['total'][0])
    col2.metric("Opérations Lancées", df_events['total'][0])
    col3.metric("Status Serveur", "ONLINE", delta="Stable")
    
    st.divider()
    
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("📢 DERNIÈRES INFOS")
        st.info("Le prochain tournoi majeur aura lieu le weekend prochain. Préparez vos teams !")
        st.image("https://images.alphacoders.com/105/1050143.jpg", use_container_width=True)
    with c_right:
        st.subheader("🥇 TOP FRAGGEURS")
        df_top = pd.read_sql_query("SELECT pseudo, MAX(kd) as Top_KD FROM performances GROUP BY pseudo ORDER BY Top_KD DESC LIMIT 5", conn)
        if not df_top.empty:
            st.table(df_top)
        else:
            st.write("Aucune donnée.")
    conn.close()

# --- 7. ONGLET : COMPÉTITION (ORGANISATION & SCRIMS) ---
with tab_compete:
    col_menu, col_display = st.columns([1, 2])
    
    with col_menu:
        st.subheader("🛠️ GESTION")
        mode = st.radio("Action", ["Voir les Matchs", "Publier un Match/Tournoi"])
        
        if mode == "Publier un Match/Tournoi":
            with st.form("new_event"):
                org = st.text_input("Pseudo Organisateur")
                type_e = st.selectbox("Catégorie", ["SCRIM AMICAL", "TOURNOI", "RANKED PUSH", "CHALLENGE"])
                title = st.text_input("Nom de l'opération")
                date_e = st.date_input("Date")
                prize = st.text_input("Récompense (ex: 1000 CP)")
                desc = st.text_area("Règles & Détails")
                
                if st.form_submit_button("LANCER L'APPEL AUX ARMES"):
                    if org and title:
                        conn = get_connection()
                        conn.execute("INSERT INTO evenements (organisateur, type, titre, date, details, cashprize, status) VALUES (?,?,?,?,?,?,?)",
                                     (org, type_e, title, str(date_e), desc, prize, "OUVERT"))
                        conn.commit()
                        conn.close()
                        st.success("Annonce publiée sur l'Arena !")
                    else:
                        st.error("Remplis les champs obligatoires !")

    with col_display:
        st.subheader("📅 OPÉRATIONS DISPONIBLES")
        conn = get_connection()
        # Sécurité : On s'assure que la table existe
        conn.execute("CREATE TABLE IF NOT EXISTS evenements (id INTEGER PRIMARY KEY, organisateur TEXT, type TEXT, titre TEXT, date TEXT, details TEXT, cashprize TEXT, status TEXT)")
        df_ev = pd.read_sql_query("SELECT * FROM evenements WHERE status = 'OUVERT'", conn)
        
        if not df_ev.empty:
            for i, row in df_ev.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #FF4D00; font-weight: bold;">{row['type']}</span>
                        <span style="color: #888;">{row['date']}</span>
                    </div>
                    <h2 style="margin: 10px 0; color: white !important;">{row['titre']}</h2>
                    <p>{row['details']}</p>
                    <div style="background: rgba(255, 77, 0, 0.1); padding: 10px; border-radius: 5px;">
                        <span style="color: #FF4D00; font-weight: bold;">💰 PRIX : {row['cashprize']}</span> | 
                        <span style="color: #EEE;">Par : {row['organisateur']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"S'inscrire à {row['titre']}"):
                    with st.form(key=f"insc_{row['id']}"):
                        p_name = st.text_input("Pseudo / Nom de Team")
                        p_cont = st.text_input("Discord ou WhatsApp")
                        if st.form_submit_button("VALIDER L'INSCRIPTION"):
                            conn.execute("INSERT INTO inscriptions VALUES (?,?,?,?)", 
                                         (row['id'], p_name, p_cont, str(datetime.date.today())))
                            conn.commit()
                            st.success(f"Soldat {p_name} inscrit !")
        else:
            st.write("Aucun match prévu. Sois le premier à organiser !")
        conn.close()

# --- 8. ONGLET : ANALYSE STATS ---
with tab_analyse:
    st.header("📊 DOSSIER DU SOLDAT")
    with st.form("stat_form"):
        col_s1, col_s2 = st.columns(2)
        p_name = col_s1.text_input("Ton Pseudo")
        p_kd = col_s2.number_input("Ton K/D Ratio", min_value=0.0, step=0.01)
        if st.form_submit_button("ENREGISTRER MES STATS"):
            if p_name:
                conn = get_connection()
                conn.execute("INSERT INTO performances VALUES (?,?,?)", (p_name, p_kd, str(datetime.date.today())))
                conn.commit()
                conn.close()
                st.success("Stats sauvegardées !")
            else:
                st.error("Pseudo requis.")

    st.divider()
    
    # Visualisation des performances
    st.subheader("📈 ÉVOLUTION DE LA COMMUNAUTÉ")
    conn = get_connection()
    df_perf = pd.read_sql_query("SELECT * FROM performances", conn)
    if not df_perf.empty:
        st.line_chart(df_perf.set_index('date')['kd'])
    else:
        st.info("Pas assez de données pour le graphique.")
    conn.close()

# --- 9. ONGLET : CONTACT & MEDIA ---
with tab_contact:
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.subheader("📺 LIVE STREAM")
        st.video("https://youtu.be/8Oyl2sQE7JI?si=SgEaZcJwlHroRSRJ")
    with c_m2:
        st.subheader("🔗 RÉSEAUX")
        st.link_button("TIKTOK", "https://www.tiktok.com/@lapoulefolle007")
        st.link_button("LINKEDIN", "https://www.linkedin.com/in/arsène-mbabeh-meye-4823a9258")
        st.info("Pour toute collaboration ou coaching : arsenemeye.mb@gmail.com")

st.markdown("<p style='text-align: center; margin-top: 50px; color: #333;'>© 2026 CODM ARENA - TOUS DROITS RÉSERVÉS</p>", unsafe_allow_html=True)