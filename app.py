import os
import shutil
import uuid
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from fastapi import FastAPI, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from agent import app_agent, SYSTEM_PROMPT
from audio_utils import AudioHandler, TEMP_DIR
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thozhan - Tamil Voice Assistant")

# Per-session conversation store
session_store: dict = {}

def get_session(session_id: str) -> list:
    if session_id not in session_store:
        session_store[session_id] = []
    return session_store[session_id]

def add_to_session(session_id: str, role: str, content: str):
    history = get_session(session_id)
    history.append((role, content))
    if len(history) > 20:
        history.pop(0)
        history.pop(0)

def get_history_as_messages(session_id: str) -> list:
    messages = []
    for role, content in get_session(session_id):
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    return messages


ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_handler = AudioHandler()

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "thozhan-voice-assistant"}


@app.post("/clear")
async def clear_session(request: Request):
    session_id = request.cookies.get("session_id", "default")
    session_store.pop(session_id, None)
    return {"status": "cleared"}


def _delete_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.post("/chat/audio")
async def chat_audio(request: Request, file: UploadFile = File(...)):
    import traceback
    session_id = request.cookies.get("session_id") or str(uuid.uuid4())

    try:
        safe_filename = f"input_{uuid.uuid4()}.wav"
        temp_path = str(TEMP_DIR / safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user_text = audio_handler.speech_to_text(temp_path)

        if not user_text:
            return JSONResponse(status_code=400, content={"error": "Could not recognize speech. Please try again."})

        add_to_session(session_id, "user", user_text)

        all_messages = [SystemMessage(content=SYSTEM_PROMPT)] + get_history_as_messages(session_id)
        inputs = {"messages": all_messages}

        outputs = await asyncio.to_thread(
            app_agent.invoke,
            inputs,
            config={"recursion_limit": 10}
        )
        last_msg = outputs["messages"][-1]
        final_response_text = last_msg.content

        add_to_session(session_id, "assistant", final_response_text)

        audio_response_path = await audio_handler.text_to_speech(final_response_text)
        filename = os.path.basename(audio_response_path)

        response = JSONResponse(content={
            "user_text": user_text,
            "agent_text": final_response_text,
            "audio_url": f"/audio/{filename}",
            "session_id": session_id
        })
        response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")
        return response

    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/audio/{filename}")
async def get_audio(filename: str, background_tasks: BackgroundTasks):
    if "/" in filename or "\\" in filename or ".." in filename:
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    path = str(TEMP_DIR / filename)
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "Audio not found"})
    background_tasks.add_task(_delete_file, path)
    return FileResponse(path)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
