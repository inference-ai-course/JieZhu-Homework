## Voice Assistant Project

### Introduction Two versions of the Voice Assistant Project
[Click here to download the video](FirstProject-VoiceAssistant.mp4)

# Voice Assistant — FastAPI & Gradio Versions

This project demonstrates a simple **speech → text → LLM → speech** pipeline with two implementations:

- **FastAPI endpoint** for other applications to call (upload audio, get audio reply).
- **Gradio UI** for direct, in-browser recording and playback.

---

## Architecture (Both Versions)

1. **ASR (speech → text)**  
   - FastAPI: `openai/whisper` via `whisper.load_model("small")`  
   - Gradio: Hugging Face pipeline `automatic-speech-recognition` with `openai/whisper-base.en`
2. **LLM (text → text)**  
   - Hugging Face Llama
3. **TTS (text → speech)**  
   - `gTTS` generates a `.wav` reply
4. **Persistence**  
   - Appends conversation to `historyConversation.txt`  
   - Saves audio files as `prompt-<timestamp>.wav` and `Response-<timestamp>.wav`

--------------------------------------------------------------------------------------------------------------------

## FastAPI Version

### What it does
- Exposes an endpoint `POST /chat/` that accepts an audio file.
- Transcribes the audio to text (Whisper).
- Generates a response with the LLM (TinyLlama).
- Converts the response text to speech (gTTS).
- Returns the **audio reply** (`audio/wav`) as the response.

### Key files produced
- `prompt-YYYY-MM-DD-HH-MM-SS.wav` — your uploaded prompt saved to disk  
- `Response-YYYY-MM-DD-HH-MM-SS.wav` — synthesized assistant reply  
- `historyConversation.txt` — appended text log of prompts and responses


--------------------------------------------------------------------------------------------------------------------
## Gradio Interface Version

### How It Works

1. **Record your voice** in the browser using Gradio’s `Audio` component.  
2. **ASR (Automatic Speech Recognition)** — Converts speech to text using  
   Hugging Face pipeline `automatic-speech-recognition` with `openai/whisper-base.en`.  
3. **LLM Response** — Generates a text reply using  
   `pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v0.6")`.  
4. **TTS (Text to Speech)** — Converts the reply text to a `.wav` audio file using `gTTS`.  
5. **Playback** — Plays the audio reply automatically in the browser.  
6. **Logging** — Saves all interactions to `historyConversation.txt` for record-keeping.  
