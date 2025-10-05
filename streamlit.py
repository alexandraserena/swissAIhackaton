import os
import io
import uuid
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from rag_apertus import answer_query_with_history
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# ----- PAGE CONFIG -----
st.set_page_config(page_title="Swiss AI Chatbot", layout="wide")

# ---------- CONFIG & KEYS ----------
load_dotenv()
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_KEY:
    st.stop()
    raise RuntimeError("ELEVENLABS_API_KEY non impostata")

client = ElevenLabs(api_key=ELEVEN_KEY)
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_FMT = "mp3_44100_128"

# ---------- HEADER ----------
st.markdown(
    """
    <style>
        .header-image { border-radius: 0 0 10px 10px; margin: 0; padding: 0; display: block; }
        .chat-container { max-height: 70vh; overflow-y: auto; padding: 10px; border: 1px solid #eee; border-radius: 10px; background-color: #f7f7f7; }
        .user-bubble { background-color: #E0E0E0; color: #000; padding: 10px; border-radius: 15px; margin: 5px 0; text-align: right; }
        .bot-bubble { background-color: #ECECEC; color: #000; padding: 10px; border-radius: 15px; margin: 5px 0; text-align: left; }
    </style>
    """,
    unsafe_allow_html=True
)
st.image("static/berna.jpg", use_container_width=True, output_format="auto")
st.title("Swiss AI 🗣️")

# ---------- LOAD CANTONS ----------
@st.cache_data
def load_cantons():
    gdf = gpd.read_file("data/cantons.geojson")
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")
    return gdf

gdf = load_cantons()
cantoni_principali = ["Zürich", "Vaud", "Neuchâtel"]

# ---------- SIDEBAR ----------
with st.sidebar:
    lang = st.selectbox(
        "Seleziona lingua / Select language / Choisir la langue / Sprache wählen",
        ["Italiano 🇮🇹", "Français 🇫🇷", "English 🇬🇧", "Deutsch 🇩🇪"]
    )

    if lang == "Italiano 🇮🇹": links_header = "### Link utili"
    elif lang == "Français 🇫🇷": links_header = "### Liens utiles"
    elif lang == "English 🇬🇧": links_header = "### Useful Links"
    elif lang == "Deutsch 🇩🇪": links_header = "### Nützliche Links"

    st.markdown(links_header)
    st.markdown("[Vaud Site](https://www.vd.ch/)")
    st.markdown("[Zurich Site](https://www.zh.ch/de/migration-integration/willkommen/english.html)")
    st.markdown("[Neuchâtel Site](https://www.ne.ch/Pages/accueil.aspx)")
    st.markdown("[Brochure](https://github.com/lucreziaabernini/swissAIhackathon/tree/main)")
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.image("static/logo.png", use_container_width=True)

# ---------- TRADUZIONI ----------
if lang == "Italiano 🇮🇹":
    placeholder_text = "Scrivi la tua domanda qui..."
    submit_text = "Invia"
    feedback_prompt = "Valuta la risposta del bot:"
    canton_mode_prompt = "Vuoi esplorare un singolo cantone o più cantoni?"
    select_cantone_subheader = "🌍 Seleziona un cantone"
    single_text = "Singolo"
    multi_text = "Libero (multi)"
    select_cantone_info = "👆 Seleziona un cantone per iniziare."
    select_more_cantons = "Seleziona uno o più cantoni:"
    welcome_text = "👋 Benvenuto! Io sono Emilie, come posso aiutarti?"
elif lang == "Français 🇫🇷":
    placeholder_text = "Écrivez votre question ici..."
    submit_text = "Envoyer"
    feedback_prompt = "Évaluez la réponse du bot :"
    canton_mode_prompt = "Voulez-vous explorer un seul canton ou plusieurs cantons?"
    select_cantone_subheader = "🌍 Sélectionnez un canton"
    single_text = "Unique"
    multi_text = "Libre (multi)"
    select_cantone_info = "👆 Sélectionnez un canton pour commencer."
    select_more_cantons = "Sélectionnez un ou plusieurs cantons:"
    welcome_text = "👋 Bienvenue ! Je suis Emilie, comment puis-je vous aider ?"
elif lang == "English 🇬🇧":
    placeholder_text = "Write your question here..."
    submit_text = "Send"
    feedback_prompt = "Rate the bot's answer:"
    canton_mode_prompt = "Do you want to explore a single canton or multiple cantons?"
    select_cantone_subheader = "🌍 Select a canton"
    single_text = "Single"
    multi_text = "Free (multi)"
    select_cantone_info = "👆 Select a canton to start."
    select_more_cantons = "Select one or more cantons:"
    welcome_text = "👋 Welcome! I am Emilie, how can I help you?"
elif lang == "Deutsch 🇩🇪":
    placeholder_text = "Schreiben Sie hier Ihre Frage..."
    submit_text = "Senden"
    feedback_prompt = "Bewerten Sie die Antwort des Bots:"
    canton_mode_prompt = "Möchten Sie einen einzelnen Kanton oder mehrere erkunden?"
    select_cantone_subheader = "🌍 Wählen Sie einen Kanton"
    single_text = "Einzeln"
    multi_text = "Frei (multi)"
    select_cantone_info = "👆 Wählen Sie einen Kanton, um zu starten."
    select_more_cantons = "Wählen Sie einen oder mehrere Kantone aus:"
    welcome_text = "👋 Willkommen! Ich bin Emilie, wie kann ich Ihnen helfen?"

st.subheader(select_cantone_subheader)

# ---------- SELEZIONE CANTONI ----------
mode = st.radio(canton_mode_prompt, [single_text, multi_text], horizontal=True)
selezionati = []

if "singolo_cantone" not in st.session_state:
    st.session_state.singolo_cantone = None

if mode == single_text:
    cols = st.columns(len(cantoni_principali))
    for i, cantone in enumerate(cantoni_principali):
        if cols[i].button(cantone):
            st.session_state.singolo_cantone = cantone
    if st.session_state.singolo_cantone:
        selezionati = [st.session_state.singolo_cantone]
elif mode == multi_text:
    selezionati = st.multiselect(
        select_more_cantons,
        options=gdf["name"].tolist(),
        default=["Zürich"]
    )

# Mostra la mappa
if selezionati:
    subset = gdf[gdf["name"].isin(selezionati)]
    bounds = subset.total_bounds
    m = folium.Map(
        location=[(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2],
        zoom_start=8, tiles="cartodb positron"
    )
    folium.GeoJson(
        subset,
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.3
        },
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Cantone:"])
    ).add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.info(select_cantone_info)

# ---------- STATE ----------
def init_state(lang: str, welcome_text: str):
    """Inizializza o aggiorna lo stato della sessione in base alla lingua."""
    if "current_lang" not in st.session_state:
        st.session_state.current_lang = lang

    # Se cambia la lingua, resetta la cronologia con il nuovo messaggio di benvenuto
    if "history" not in st.session_state or st.session_state.current_lang != lang:
        st.session_state.history = [{
            "id": str(uuid.uuid4()),
            "user": "",
            "bot": welcome_text
        }]
        st.session_state.current_lang = lang

    if "audio_bytes" not in st.session_state:
        st.session_state.audio_bytes = {}

    if "feedback_count" not in st.session_state:
        st.session_state.feedback_count = 0

# Chiamata subito dopo aver determinato `lang` e `welcome_text`
init_state(lang, welcome_text)


# ---------- Helper TTS ----------
def tts_to_mp3_bytes(text: str) -> bytes | None:
    if not text or not text.strip():
        return None
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FMT,
        )
        if hasattr(audio, "read"):
            return audio.read()
        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)
        if hasattr(audio, "__iter__"):
            chunks = [c for c in audio if isinstance(c, (bytes, bytearray))]
            return b"".join(chunks) if chunks else None
    except Exception:
        pass
    try:
        audio_stream = client.text_to_speech.stream(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
        )
        chunks = [c for c in audio_stream if isinstance(c, (bytes, bytearray))]
        return b"".join(chunks) if chunks else None
    except Exception as e:
        raise e

# ---------- LAYOUT CHAT ----------
col_chat, col_side = st.columns([3, 1])
with col_chat:
    chat_placeholder = st.empty()

    def render_chat():
        with chat_placeholder.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for idx, msg in enumerate(st.session_state.history):
                if msg["user"]:
                    st.markdown(f'<div class="user-bubble">👤 Me: {msg["user"]}</div>', unsafe_allow_html=True)
                bot_col1, bot_col2 = st.columns([0.9, 0.1])
                with bot_col1:
                    st.markdown(f'<div class="bot-bubble">🗣️ Emilie: {msg["bot"]}</div>', unsafe_allow_html=True)
                with bot_col2:
                    if st.button("▶️", key=f"play_{msg['id']}_{idx}"):
                        mp3_bytes = tts_to_mp3_bytes(msg["bot"])
                        if mp3_bytes and len(mp3_bytes) > 100:
                            st.session_state.audio_bytes[msg["id"]] = mp3_bytes
                        else:
                            st.warning("Audio vuoto o non valido")
                if msg["id"] in st.session_state.audio_bytes:
                    st.audio(io.BytesIO(st.session_state.audio_bytes[msg["id"]]), format="audio/mp3")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------- FORM INPUT ----------
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(placeholder_text)
        submit_button = st.form_submit_button(submit_text)
        if submit_button and user_input:
            try:
                risposta = answer_query_with_history(user_input)
            except Exception as e:
                risposta = f"Errore nella generazione della risposta: {str(e)}"
            st.session_state.history.append({"id": str(uuid.uuid4()), "user": user_input, "bot": risposta})
            st.session_state.feedback_count += 1

    render_chat()

    # ---------- FEEDBACK OGNI 5 RISPOSTE ----------
    if st.session_state.feedback_count > 0 and st.session_state.feedback_count % 1 == 0:
        st.markdown(f"**{feedback_prompt}**")
        feedback_cols = st.columns(6)
        for i, col in enumerate(feedback_cols):
            if col.button("⭐"*i, key=f"feedback_{i}"):
                st.success(f"Grazie per il tuo feedback: {i} ⭐")
                st.session_state.feedback_count = 0
