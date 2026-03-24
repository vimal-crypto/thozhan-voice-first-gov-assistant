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
    print("   FFMPEG paths added via static-ffmpeg")
except ImportError:
    print("   static-ffmpeg not found, please pip install static-ffmpeg")

from fastapi import FastAPI, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Flat imports — all files are at root level (no voice_agent package)
from audio_utils import AudioHandler, TEMP_DIR
from agent import app_agent, SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# FIX 3: Configure log levels explicitly so Uvicorn INFO messages are not
# incorrectly captured as severity=error by the deployment platform.
logging.basicConfig(level=logging.INFO)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tamil Voice Agent - Thozhan")

# --- Per-session conversation isolation ---
# Each session_id maps to its own conversation history
session_store: dict[str, list] = {}

def get_session(session_id: str) -> list:
    if session_id not in session_store:
        session_store[session_id] = []
    return session_store[session_id]

def add_to_session(session_id: str, role: str, content: str):
    history = get_session(session_id)
    history.append((role, content))
    # Keep last 20 messages per session
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


# Restrict CORS to specific origins in production
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
    """Background task to delete a file after it has been served."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"[CLEANUP] Deleted served audio: {os.path.basename(path)}")
    except Exception as e:
        logger.warning(f"[CLEANUP] Could not delete {path}: {e}")


@app.post("/chat/audio")
async def chat_audio(request: Request, file: UploadFile = File(...)):
    import traceback

    # Get or create session ID from cookie
    session_id = request.cookies.get("session_id") or str(uuid.uuid4())

    try:
        logger.info("[SERVER] Received audio file, starting processing...")

        # Sanitize filename to prevent path traversal
        safe_filename = f"input_{uuid.uuid4()}.wav"
        temp_path = str(TEMP_DIR / safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"[SERVER] Saved file to: {temp_path}")

        logger.info("[SERVER] Starting Speech-to-Text...")
        user_text = audio_handler.speech_to_text(temp_path)
        logger.info(f"[SERVER] STT Result: {len(user_text)} chars")

        # FIX 2: Guard against empty or whitespace-only STT result.
        # Google STT may return empty string for silence or unintelligible audio.
        if not user_text or not user_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "உங்கள் குரல் புரியவில்லை. தெளிவாக பேசி மீண்டும் முயற்சிக்கவும். (Could not recognize speech. Please speak clearly and try again.)"}
            )

        add_to_session(session_id, "user", user_text)

        all_messages = [SystemMessage(content=SYSTEM_PROMPT)] + get_history_as_messages(session_id)
        inputs = {"messages": all_messages}

        logger.info("[AGENT] Invoking agent...")
        outputs = await asyncio.to_thread(
            app_agent.invoke,
            inputs,
            config={"recursion_limit": 10}
        )
        last_msg = outputs["messages"][-1]
        final_response_text = last_msg.content

        add_to_session(session_id, "assistant", final_response_text)
        logger.info(f"[AGENT] Replied: {len(final_response_text)} chars")

        logger.info("[SERVER] Starting Text-to-Speech...")
        audio_response_path = await audio_handler.text_to_speech(final_response_text)
        logger.info(f"[SERVER] TTS complete: {audio_response_path}")

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
        logger.error(f"[ERROR] Exception in chat_audio: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/audio/{filename}")
async def get_audio(filename: str, background_tasks: BackgroundTasks):
    # Sanitize: only allow safe filenames (no path traversal)
    if "/" in filename or "\\" in filename or ".." in filename:
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    path = str(TEMP_DIR / filename)
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "Audio file not found"})
    # Delete after serving
    background_tasks.add_task(_delete_file, path)
    return FileResponse(path)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
