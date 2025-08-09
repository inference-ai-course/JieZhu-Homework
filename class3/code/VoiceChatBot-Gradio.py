import gradio as gr
import datetime
import numpy as np
from transformers import pipeline
from gtts import gTTS
import whisper

asr_model = whisper.load_model("small")
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v0.6")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def asr_transcribe(audio):
    sr, y = audio    
    # Convert to mono if stereo
    if y.ndim > 1:
        y = y.mean(axis=1)        
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    result = transcriber({"sampling_rate": sr, "raw": y})
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

def voice_assistant(audio, history_state):
    if audio is None:
        return "Please record a message first.", None    
    user_text = asr_transcribe(audio)
    if not user_text:
        return "I couldn’t recognize any speech. Try again.", None        
    bot_text = generate_response(user_text)
    audio_path = synthesize_speech(bot_text)
    history_state.append(gr.State([bot_text, audio_path]))
    return bot_text,audio_path,history_state    

with gr.Blocks(theme="soft") as demo:
    gr.Markdown("## English Voice Assistant (Gradio + Whisper + LLM + TTS)")
    mic = gr.Audio(sources=["microphone"], label="Record your Prompt")
    send = gr.Button("Send")
    out_text = gr.Textbox(label="Assistant (text output)")
    out_audio = gr.Audio(label="Assistant (voice output)", autoplay=True)
    history_state = gr.State([])
    send.click(voice_assistant, inputs=[mic, history_state], outputs=[out_text, out_audio,history_state])

if __name__ == "__main__":
    demo.launch()