from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import json, os
from datetime import datetime

router = APIRouter()
DB_FILE = "company_jobs.json"

def load_jobs():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(DB_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

class JobPost(BaseModel):
    company: str
    role: str
    type: str
    description: str
    questions: List[str]

@router.post("/post")
def post_job(job: JobPost):
    jobs = load_jobs()
    entry = { **job.dict(), "id": len(jobs) + 1, "posted_at": datetime.now().isoformat() }
    jobs.append(entry)
    save_jobs(jobs)
    return entry

@router.get("/jobs")
def get_jobs():
    return load_jobs()

class StudentPref(BaseModel):
    name: str
    role: str
    company: str
    type: str

@router.post("/student/preference")
def save_preference(pref: StudentPref):
    prefs = []
    if os.path.exists("student_prefs.json"):
        with open("student_prefs.json") as f:
            prefs = json.load(f)
    prefs.append({**pref.dict(), "saved_at": datetime.now().isoformat()})
    with open("student_prefs.json", "w") as f:
        json.dump(prefs, f, indent=2)
    return {"status": "saved"}