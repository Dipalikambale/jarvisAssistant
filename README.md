# JARVIS AI Voice Assistant

A modular Python voice assistant with a microphone-driven CLI and a Streamlit
web interface. It combines Google Speech Recognition, offline `pyttsx3`
speech, browser-playable gTTS audio, Wikipedia lookups, safe system-app
launching, and optional Google Gemini conversation.

## Features

- **Voice input:** CLI microphone capture with SpeechRecognition/PyAudio;
  browser microphone recording in Streamlit.
- **Voice output:** offline `pyttsx3` in the CLI and optional gTTS playback in
  the browser.
- **Built-in commands:** date/time, Wikipedia summaries, Google searches,
  Google Calendar, YouTube, Calculator, Notepad, and local music playback.
- **Conversational AI:** Gemini responses with recent conversation context.
  Gemini is optional; built-in commands work without an API key.
- **Safety:** system applications are selected from a fixed allowlist; no
  user-provided shell commands are executed.
- **Structured logs:** JSON log records are written to `logs/application.log`.
  User prompts and transcripts are not written to logs.

## Setup

Use Python 3.10 or newer. From this directory, create and activate a virtual
environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PyAudio is optional and only needed for microphone input in the CLI. The
Streamlit interface uses the browser's microphone and does not open the server
machine's microphone. To enable CLI microphone input, install the optional
requirements:

```powershell
pip install -r requirements-cli.txt
```

On Windows, PyAudio may need to compile native code if a prebuilt wheel is not
available for your Python version. The build error mentioning "Microsoft
Visual C++ 14.0 or greater" means the C++ Build Tools are missing; install
Microsoft C++ Build Tools or use a Python version for which a compatible
PyAudio wheel is available. You can still run the Streamlit app without
PyAudio.

Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` to enable Gemini. The
default model is `gemini-3.8-flash`. Keep your actual API key only in `.env`;
never place it in `.env.example` or commit it. The key is optional for built-in
assistant commands. Optionally set `MUSIC_DIR` to a folder containing audio
files (`.mp3`, `.wav`, `.ogg`, `.m4a`, or `.flac`).

## Run

Start the command-line voice assistant (install `requirements-cli.txt` first
for microphone input):

```powershell
python main.py
```

Start the web assistant:

```powershell
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) using the
   GitHub account that can access the repository.
3. Choose **Create app**, select `Dipalikambale/jarvisAssistant`, branch
   `main`, and main file path `streamlit_app.py`.
4. In the deployment's **Advanced settings / Secrets**, add:

   ```toml
   GOOGLE_API_KEY = "your-new-Google-AI-Studio-key"
   GEMINI_MODEL = "gemini-3.8-flash"
   ```

5. Deploy the app. Keep the API key in Streamlit Secrets; do not commit it to
   GitHub. Streamlit Cloud secrets are supported directly by this app.

The Streamlit app uses the visitor's browser for microphone capture. As with
local usage, speech transcription and optional gTTS responses call external
Google services.

Say or type `help` for example commands. Say `exit`, `quit`, or `stop` to end
the CLI session.

## Example commands

- "What time is it?"
- "Wikipedia search Ada Lovelace"
- "Open calculator" / "Open notepad"
- "Open Google Calendar" / "Open YouTube"
- "Search Google for Python speech recognition"
- "Play music"
- Ask a general question (requires `GOOGLE_API_KEY`)

## Project layout

```text
jarvis_assistant/
  actions.py             Allowlisted apps, URLs, and local music playback
  assistant.py           Intent routing and conversation orchestration
  cli.py                 Microphone-driven command-line interface
  config.py              Environment-based settings
  gemini_client.py       Optional Gemini API integration
  logging_config.py      JSON logging configuration
  speech.py              Speech-to-text and text-to-speech adapters
  wikipedia_service.py   Wikipedia API integration
streamlit_app.py         Browser-based chat and voice interface
main.py                  CLI entry point
tests/                   Offline unit tests
```

## Privacy and external services

Microphone recordings are sent to Google's speech recognition service when
transcribed. Gemini receives prompts and the recent conversation when enabled.
Wikipedia queries and gTTS speech text are sent to their respective services.
Use typed input and disable spoken responses in the web app if you do not want
to use those voice services. This project does not log prompt or transcript
contents.

## Test

Run the offline unit tests with:

```powershell
python -m unittest discover -s tests -v
```
