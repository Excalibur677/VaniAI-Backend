import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            response = await client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="en",
                prompt="Indian student interview answer, may contain Hinglish.",
            )
        return response.text
    except Exception as e:
        print(f"Whisper error: {e}")
        return "Transcript unavailable."