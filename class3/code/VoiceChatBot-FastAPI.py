import datetime
import whisper
from transformers import pipeline
from gtts import gTTS
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

asr_model = whisper.load_model("small")
llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v0.6")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def transcribe_audio(audio_bytes):    
    filename = f"prompt-{timestamp}.wav"    
    # Save to audio file
    with open(filename, "wb") as f:
        f.write(audio_bytes)    
    # Audio to Text
    result = asr_model.transcribe(filename)
    return result["text"] 

def generate_response(user_text):
    # Define the file path
    file_path = "historyConversation.txt"
    # The prompt  
    messages = [{"role": "user", "content": user_text},]

    prompt = f"user: {user_text}\n"       
    outputs = llm(messages, max_new_tokens=100)
    #print(outputs)
    bot_response = outputs[0]["generated_text"]    
    #print(bot_response)  
    # Open the file in append mode ("a")
    with open(file_path, "a", encoding="utf-8") as file:   
        file.write(f"Datetime: {timestamp}\n") 
        file.write(f"{prompt}\n")     
        file.write(f"assistant: {bot_response[1]["content"]}\n")
    return bot_response[1]["content"]    

def synthesize_speech(text):    
    filename = f"Response-{timestamp}.wav"    
    # Text to Audio
    tts = gTTS(text, lang='en')
    tts.save(filename)
    return filename
    
app = FastAPI()

@app.post("/chat/")
async def chat_endpoint(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    user_text = transcribe_audio(audio_bytes)
    bot_text = generate_response(user_text)
    audio_path = synthesize_speech(bot_text)
    return FileResponse(audio_path, media_type="audio/wav", filename = audio_path)