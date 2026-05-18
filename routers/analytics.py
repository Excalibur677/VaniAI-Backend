from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def summary():
    return {
        "message": "Session analytics endpoint ready.",
        "pillars": ["empathy", "articulation", "grammar", "structure"]
    }
