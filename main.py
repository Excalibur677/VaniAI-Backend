from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import interview, analytics, company
from routers import interview, analytics
from routers import interview, analytics, company, admin
from fastapi import Request
import json, os

load_dotenv()

app = FastAPI(title="VaniAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(company.router, prefix="/company", tags=["Company"])
app.include_router(interview.router, prefix="/interview", tags=["Interview"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

COUNTER_FILE = "student_count.json"

def get_count():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            return json.load(f).get("count", 0)
    return 0

def increment_count():
    count = get_count() + 1
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": count}, f)
    return count

@app.get("/")
def root():
    return {"status": "VaniAI backend running"}

@app.post("/counter/increment")
def increment():
    return {"count": increment_count()}

@app.get("/counter")
def counter():
    return {"count": get_count()}

@app.post("/student/preference")
async def student_pref(request: Request):
    from routers.company import save_preference, StudentPref
    data = await request.json()
    return save_preference(StudentPref(**data))