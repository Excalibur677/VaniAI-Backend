from fastapi import APIRouter
from fastapi.responses import FileResponse
import os, json

router = APIRouter()
SESSIONS_DIR = "sessions"

@router.get("/sessions")
def get_sessions():
    if not os.path.exists(SESSIONS_DIR):
        return []
    result = []
    for folder in os.listdir(SESSIONS_DIR):
        txt = os.path.join(SESSIONS_DIR, folder, "transcript.txt")
        if os.path.exists(txt):
            with open(txt, encoding="utf-8") as f:
                lines = f.readlines()
            def val(prefix):
                for l in lines:
                    if l.startswith(prefix):
                        return l.replace(prefix, "").strip()
                return "N/A"
            result.append({
                "session_id": folder,
                "date": folder[:8],
                "transcript": val("Transcript:"),
                "overall": val("Overall:"),
                "wpm": val("WPM:"),
                "fillers": val("Fillers:"),
            })
    return sorted(result, key=lambda x: x["date"], reverse=True)

@router.get("/download/{session_id}")
def download(session_id: str):
    path = os.path.join(SESSIONS_DIR, session_id, "transcript.txt")
    if os.path.exists(path):
        return FileResponse(path, filename=f"{session_id}_transcript.txt")
    return {"error": "Not found"}