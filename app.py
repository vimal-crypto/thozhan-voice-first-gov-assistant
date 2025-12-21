import os
import shutil
import uuid
import logging
import asyncio
from collections import defaultdict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    print("   FFMPEG paths added via static-ffmpeg")
except ImportError:
    print("   static-ffmpeg not found, please pip install static-ffmpeg")

if "GROQ_API_KEY" not in os.environ:
    raise EnvironmentError(
        "❌ GROQ_API_KEY not found!\n"
        "Please set it in .env file or as environment variable.\n"
        "Get your FREE key at: https://console.groq.com/"
    )
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from voice_agent.audio_utils import AudioHandler
from voice_agent.agent import app_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from voice_agent.agent import SYSTEM_PROMPT

app = FastAPI(title="Tamil Voice Agent")

conversation_history = []

user_profile = {
    "age": None,
    "income": None,
    "occupation": None,
    "location": None
}

def clear_conversation():
    global conversation_history, user_profile
    conversation_history = []
    user_profile = {"age": None, "income": None, "occupation": None, "location": None}

def add_to_history(role: str, content: str):
    conversation_history.append((role, content))
    if len(conversation_history) > 20:
        conversation_history.pop(0)
        conversation_history.pop(0)

def get_history_as_messages():
    messages = []
    for role, content in conversation_history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    return messages


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_handler = AudioHandler()

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/clear")
async def clear_session():
    clear_conversation()
    return {"status": "cleared"}


@app.post("/chat/audio")
async def chat_audio(file: UploadFile = File(...)):
    import traceback
    
    try:
        print("[SERVER] Received audio file, starting processing...")
        
        temp_filename = f"input_{file.filename}"
        temp_path = os.path.join("voice_agent", "temp_audio", temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"[SERVER] Saved file to: {temp_path}")
        
        print("[SERVER] Starting Speech-to-Text...")
        user_text = audio_handler.speech_to_text(temp_path)
        print(f"[SERVER] STT Result: (detected {len(user_text)} chars)")
        
        if not user_text:
            return JSONResponse(status_code=400, content={"error": "Could not recognize speech. Try again."})

        print(f"[AGENT] Thinking on: (Tamil text - {len(user_text)} chars)")
        
        add_to_history("user", user_text)
        
        all_messages = [SystemMessage(content=SYSTEM_PROMPT)] + get_history_as_messages()
        inputs = {"messages": all_messages}
        
        print(f"[AGENT] Conversation history: {len(conversation_history)} messages")
        
        print("[AGENT] Invoking agent...")
        outputs = await asyncio.to_thread(
            app_agent.invoke, 
            inputs, 
            config={"recursion_limit": 5}
        )
        last_msg = outputs["messages"][-1]
        final_response_text = last_msg.content
        
        add_to_history("assistant", final_response_text)
        
        print(f"[AGENT] Replied: (Tamil text - {len(final_response_text)} chars)")

        print("[SERVER] Starting Text-to-Speech...")
        audio_response_path = await audio_handler.text_to_speech(final_response_text)
        print(f"[SERVER] TTS complete: {audio_response_path}")
        
        filename = os.path.basename(audio_response_path)
        return {
            "user_text": user_text,
            "agent_text": final_response_text,
            "audio_url": f"/audio/{filename}"
        }
        
    except Exception as e:
        print(f"[ERROR] Exception in chat_audio: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    path = os.path.join("voice_agent", "temp_audio", filename)
    return FileResponse(path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

