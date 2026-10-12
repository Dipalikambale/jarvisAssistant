import hashlib

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from jarvis_assistant.assistant import Assistant
from jarvis_assistant.config import Settings
from jarvis_assistant.logging_config import configure_logging
from jarvis_assistant.speech import synthesize_speech, transcribe_audio_file

configure_logging()
try:
    cloud_secrets = st.secrets
except StreamlitSecretNotFoundError:
    cloud_secrets = None
settings = Settings.from_environment(streamlit_secrets=cloud_secrets)
st.set_page_config(
    page_title="JARVIS | Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    :root {
        --jarvis-ink: #eaf1ff;
        --jarvis-muted: #9aa9c2;
        --jarvis-cyan: #63e6e2;
        --jarvis-blue: #7c9cff;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 70% -10%, rgba(57, 105, 166, .23), transparent 44%),
            linear-gradient(145deg, #0b1120 0%, #101729 52%, #0b1221 100%);
        color: var(--jarvis-ink);
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    [data-testid="stHeader"] { background: rgba(9, 15, 28, .72); }
    [data-testid="stMain"] .block-container {
        max-width: 1080px;
        padding-top: 2.5rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111b2d 0%, #0d1525 100%);
        border-right: 1px solid rgba(145, 174, 215, .12);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--jarvis-muted);
        font-size: .91rem;
        line-height: 1.55;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: .8rem;
        margin: .2rem 0 2.1rem;
    }
    .brand-mark {
        width: 45px;
        height: 45px;
        display: grid;
        place-items: center;
        border: 1px solid rgba(99, 230, 226, .52);
        border-radius: 15px;
        background: linear-gradient(145deg, rgba(99, 230, 226, .18), rgba(124, 156, 255, .14));
        box-shadow: 0 0 26px rgba(99, 230, 226, .13);
        font-size: 1.35rem;
    }
    .brand-name {
        color: var(--jarvis-ink);
        font: 700 1.15rem 'Segoe UI', Arial, sans-serif;
        letter-spacing: .11em;
    }
    .brand-caption {
        color: var(--jarvis-muted);
        font-size: .75rem;
        letter-spacing: .04em;
    }
    .side-label {
        color: #72839e;
        font-size: .7rem;
        font-weight: 700;
        letter-spacing: .15em;
        margin: 1.3rem 0 .55rem;
        text-transform: uppercase;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.2rem;
        border: 1px solid rgba(137, 171, 222, .19);
        border-radius: 25px;
        background: linear-gradient(115deg, rgba(29, 48, 75, .94), rgba(20, 31, 53, .82));
        box-shadow: 0 20px 55px rgba(0, 0, 0, .17);
        margin-bottom: 1.3rem;
    }
    .hero:after {
        content: '';
        position: absolute;
        width: 280px;
        height: 280px;
        right: -95px;
        top: -150px;
        border: 1px solid rgba(99, 230, 226, .18);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(99, 230, 226, .025),
                    0 0 0 58px rgba(99, 230, 226, .02);
    }
    .eyebrow {
        color: var(--jarvis-cyan);
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .17em;
        text-transform: uppercase;
    }
    .hero h1 {
        color: #f2f6ff;
        font: 700 clamp(2rem, 4vw, 3rem) 'Segoe UI', Arial, sans-serif;
        letter-spacing: -.045em;
        line-height: 1.1;
        margin: .65rem 0 .6rem;
    }
    .hero p {
        color: #aab8cd;
        font-size: 1rem;
        margin: 0;
        max-width: 620px;
    }
    .status-row {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.25rem;
    }
    .status-chip {
        padding: .38rem .7rem;
        border: 1px solid rgba(164, 188, 222, .16);
        border-radius: 999px;
        background: rgba(9, 17, 31, .38);
        color: #c6d2e4;
        font-size: .77rem;
    }
    .section-title {
        color: #edf3ff;
        font: 600 1.05rem 'Segoe UI', Arial, sans-serif;
        margin: 1.35rem 0 .2rem;
    }
    .section-subtitle {
        color: var(--jarvis-muted);
        font-size: .88rem;
        margin-bottom: .85rem;
    }
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(145, 174, 215, .11);
        border-radius: 18px;
        background: rgba(24, 36, 57, .74);
        padding: 1rem 1.1rem;
        margin-bottom: .8rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: rgba(33, 53, 79, .72);
    }
    [data-testid="stChatInput"] {
        border: 1px solid rgba(99, 230, 226, .28);
        border-radius: 16px;
        background: rgba(16, 26, 43, .96);
        box-shadow: 0 10px 35px rgba(0, 0, 0, .2);
    }
    [data-testid="stAudioInput"] {
        border: 1px solid rgba(145, 174, 215, .15);
        border-radius: 16px;
        background: rgba(20, 31, 50, .82);
        padding: .45rem .7rem;
    }
    [data-testid="stAudioInput"] label {
        color: #dce7f8;
        font-weight: 600;
    }
    [data-testid="stAudio"] { margin-top: .5rem; }
    .stButton > button {
        min-height: 3.2rem;
        width: 100%;
        border: 1px solid rgba(145, 174, 215, .17);
        border-radius: 14px;
        background: rgba(24, 37, 58, .82);
        color: #dce7f8;
        text-align: left;
        transition: border-color .18s ease, transform .18s ease, background .18s ease;
    }
    .stButton > button:hover {
        border-color: rgba(99, 230, 226, .58);
        background: rgba(35, 55, 78, .94);
        color: white;
        transform: translateY(-2px);
    }
    hr { border-color: rgba(145, 174, 215, .12); }
    @media (max-width: 700px) {
        [data-testid="stMain"] .block-container { padding: 1.2rem 1rem 1.5rem; }
        .hero { padding: 1.45rem 1.3rem; border-radius: 19px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">✦</div>
            <div>
                <div class="brand-name">J.A.R.V.I.S.</div>
                <div class="brand-caption">PERSONAL AI ASSISTANT</div>
            </div>
        </div>
        <div class="side-label">Preferences</div>
        """,
        unsafe_allow_html=True,
    )
    speak_responses = st.checkbox("Read responses aloud", value=True)
    st.caption("Voice transcription is processed using Google Speech Recognition.")
    st.markdown('<div class="side-label">AI connection</div>', unsafe_allow_html=True)
    if settings.api_key:
        st.success("Gemini connected")
        st.caption(f"Model: `{settings.gemini_model}`")
    else:
        st.warning(
            "Gemini is not configured. Add GOOGLE_API_KEY to the project .env "
            "file and restart Streamlit."
        )
    st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
    st.caption(f"{len(st.session_state.messages)} messages in this conversation")
    if st.session_state.messages and st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("last_audio_hash", None)
        st.rerun()


st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">YOUR INTELLIGENT VOICE COMPANION</div>
        <h1>Good to see you.</h1>
        <p>Ask a question, explore an idea, or tell JARVIS what you need.</p>
        <div class="status-row">
            <span class="status-chip">◉ Voice input</span>
            <span class="status-chip">⌁ Text chat</span>
            <span class="status-chip">✦ Gemini optional</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


def submit_message(prompt: str) -> None:
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": cleaned_prompt})
    history = st.session_state.messages[:-1]
    with st.chat_message("user"):
        st.markdown(cleaned_prompt)
    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("JARVIS is thinking..."):
                response = Assistant(settings).reply(cleaned_prompt, history=history)
            st.markdown(response)
            if speak_responses:
                st.audio(synthesize_speech(response), format="audio/mp3")
        except (RuntimeError, ValueError) as error:
            response = f"Sorry, I couldn't complete that request: {error}"
            st.error(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()


if st.session_state.messages:
    st.markdown('<div class="section-title">Conversation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Your recent messages with JARVIS</div>',
        unsafe_allow_html=True,
    )
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "🧑"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
else:
    st.markdown('<div class="section-title">Try asking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Choose a suggestion or start with your own message.</div>',
        unsafe_allow_html=True,
    )
    suggestion_columns = st.columns(3)
    suggestions = (
        ("◷  Tell me the time", "What time is it?"),
        ("⌕  Explore a topic", "Wikipedia search Ada Lovelace"),
        ("✧  Meet your assistant", "Tell me about yourself"),
    )
    for column, (label, prompt) in zip(suggestion_columns, suggestions):
        with column:
            if st.button(label, key=f"suggestion_{prompt}", use_container_width=True):
                submit_message(prompt)

st.markdown('<div class="section-title">Talk to JARVIS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Record a voice note or type below. You can use either input.</div>',
    unsafe_allow_html=True,
)
audio = st.audio_input("Record a voice message", label_visibility="collapsed")
if audio is not None:
    audio_hash = hashlib.sha256(audio.getvalue()).hexdigest()
    if st.session_state.get("last_audio_hash") != audio_hash:
        st.session_state.last_audio_hash = audio_hash
        try:
            submit_message(transcribe_audio_file(audio))
        except (RuntimeError, ValueError) as error:
            st.error(f"Sorry, I couldn't transcribe that recording: {error}")

typed_prompt = st.chat_input("Message JARVIS…")
if typed_prompt:
    submit_message(typed_prompt)
