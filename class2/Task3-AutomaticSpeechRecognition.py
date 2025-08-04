import os
import yt_dlp
import whisper
import json

# Step 1: Download audio from YouTube
url = "https://www.youtube.com/watch?v=j86dP_05_o0"
output_file = "downloaded_audio.%(ext)s"

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': output_file,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
    'quiet': False,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

# Step 2: Transcribe using Whisper
audio_path = "downloaded_audio.wav"
if not os.path.exists(audio_path):
    raise FileNotFoundError("Audio file not found. Check yt-dlp output.")

# Load Whisper model (you can also use "medium" or "large" if you have GPU)
model = whisper.load_model("base")

print("🔊 Transcribing audio... This may take a few minutes.")
result = model.transcribe(audio_path)

# Save transcription to file
with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("✅ Transcription saved to transcription.txt")

# Save segments to .jsonl
with open("transcription_segments.jsonl", "w", encoding="utf-8") as f:
    for segment in result["segments"]:
        json_line = {
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        }
        f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

print("✅ Saved to transcription_segments.jsonl")
