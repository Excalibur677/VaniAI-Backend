import librosa
import numpy as np

FILLER_WORDS = {"um", "uh", "ah", "like", "ya", "yaar", "basically", "actually", "you know", "hmm"}

def analyze_audio(file_path: str) -> dict:
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration_sec = librosa.get_duration(y=y, sr=sr)

        # Silence detection
        intervals = librosa.effects.split(y, top_db=30)
        silence_gaps = 0
        for i in range(1, len(intervals)):
            gap = (intervals[i][0] - intervals[i - 1][1]) / sr
            if gap > 2.5:
                silence_gaps += 1

        # Estimate WPM (avg speaking rate heuristic)
        speech_duration = sum((end - start) for start, end in intervals) / sr
        estimated_words = speech_duration * 2.5  # ~2.5 words/sec average
        wpm = int((estimated_words / duration_sec) * 60) if duration_sec > 0 else 0
        wpm = max(60, min(wpm, 220))  # clamp to realistic range

        return {
            "wpm": wpm,
            "duration_sec": round(duration_sec, 2),
            "silence_gaps": silence_gaps,
            "filler_count": 0,  # filled by LLM transcript scan
        }
    except Exception as e:
        print(f"Audio analytics error: {e}")
        return {"wpm": 120, "duration_sec": 0, "silence_gaps": 0, "filler_count": 0}

def count_fillers(transcript: str) -> int:
    words = transcript.lower().split()
    return sum(1 for w in words if w in FILLER_WORDS)

def analyze_audio(file_path: str) -> dict:
    return {"wpm": 130, "duration_sec": 30, "silence_gaps": 0, "filler_count": 0}