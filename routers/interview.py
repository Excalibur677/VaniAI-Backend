from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from services.whisper_service import transcribe_audio
from services.audio_analytics import analyze_audio
from services.llm_evaluator import evaluate_answer
import tempfile, os, json
from datetime import datetime
from fastapi import Request
import os
router = APIRouter()
SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

@router.post("/evaluate")
async def evaluate(audio: UploadFile = File(...), question: str = Form(...)):
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = os.path.join(SESSIONS_DIR, session_id)
    os.makedirs(session_folder, exist_ok=True)

    # Save audio file
    audio_path = os.path.join(session_folder, "answer.webm")
    audio_bytes = await audio.read()
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # Save to temp for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        transcript = await transcribe_audio(tmp_path)
        audio_metrics = analyze_audio(tmp_path)
        llm_result = await evaluate_answer(question, transcript)

        result = {
    "transcript": transcript,
    "wpm": audio_metrics["wpm"],
    "fillers": audio_metrics["filler_count"],
    "silence_gaps": audio_metrics["silence_gaps"],
    "scores": llm_result["scores"],
    "hinglish_corrections": llm_result["hinglish_corrections"],
    "overall": llm_result["overall"],
    "tips": llm_result.get("tips", []),  # ADD THIS
}

        # Save transcript + result as text file
        txt_path = os.path.join(session_folder, "transcript.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Question: {question}\n\n")
            f.write(f"Transcript: {transcript}\n\n")
            f.write(f"Scores: {json.dumps(llm_result['scores'], indent=2)}\n\n")
            f.write(f"Overall: {llm_result['overall']}\n")
            f.write(f"WPM: {audio_metrics['wpm']}\n")
            f.write(f"Fillers: {audio_metrics['filler_count']}\n")
            f.write(f"Silence Gaps: {audio_metrics['silence_gaps']}\n")

        return result
    finally:
        os.unlink(tmp_path)

@router.get("/questions")
def get_questions():
    return {
        "questions": [
            "Tell me about yourself and your career goals.",
            "Describe a challenge you faced and how you handled it.",
            "Why should we hire you for this role?",
            "Where do you see yourself in 5 years?",
            "What are your key strengths and one weakness?",
        ]
    }


@router.post("/speak")
async def speak_text(request: Request):
    from fastapi.responses import Response
    import httpx, base64, os
    data = await request.json()
    text = data.get("text", "")
    lang = data.get("lang", "en-IN")

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={
                "api-subscription-key": os.getenv("SARVAM_API_KEY"),
                "Content-Type": "application/json"
            },
            json={
                "inputs": [text],
                "target_language_code": lang,
                "speaker": "anushka",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.0,
                "model": "bulbul:v2"
            }
        )
        print("Sarvam response:", res.text)  # debug
        result = res.json()
        # try both possible keys
        audio_b64 = result.get("audios", [None])[0] or result.get("audio", "")
        if not audio_b64:
            return {"error": "No audio returned", "raw": result}
        audio_data = base64.b64decode(audio_b64)
        return Response(content=audio_data, media_type="audio/wav")