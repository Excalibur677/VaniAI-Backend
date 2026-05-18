import os, json
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a strict NSDC (National Skill Development Corporation) certified interview evaluator.

Evaluate the candidate's answer and return ONLY valid JSON:
{
  "scores": {
    "empathy": <1-100>,
    "articulation": <1-100>,
    "grammar": <1-100>,
    "structure": <1-100>
  },
  "overall": <exact average of 4 scores>,
  "hinglish_corrections": [
    {"original": "<hindi/regional word used>", "suggestion": "<professional english alternative>"}
  ],
  "tips": [
    "<specific improvement tip based on actual answer>"
  ]
}

STRICT NSDC RUBRIC:
- empathy (Customer Empathy & Tone):
  90-100: Warm, customer-first, emotionally intelligent
  70-89: Friendly but lacks depth
  50-69: Neutral, robotic tone
  below 50: Cold, dismissive

- articulation (Technical/Domain Articulation):
  90-100: Crystal clear, domain-specific vocabulary
  70-89: Clear but generic
  50-69: Vague, lacks examples
  below 50: Incoherent

- grammar (Grammatical Integrity):
  90-100: Perfect grammar, no errors
  70-89: Minor errors
  50-69: Frequent errors
  below 50: Hard to understand

- structure (Sentence Structure & Control):
  90-100: Clear intro, body, conclusion
  70-89: Logical but weak conclusion
  50-69: Jumbled, no clear flow
  below 50: No structure

overall: MUST be exactly (empathy + articulation + grammar + structure) / 4 rounded to integer.
tips: Give 3 specific tips based on what the candidate ACTUALLY said. Not generic advice.
hinglish_corrections: Only flag actual Hindi/regional words found in transcript.
Return ONLY JSON. No markdown. No explanation.
"""

async def evaluate_answer(question: str, transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}\n\nCandidate Answer: {transcript}"},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        # Force correct overall calculation
        sc = result["scores"]
        result["overall"] = round((sc["empathy"] + sc["articulation"] + sc["grammar"] + sc["structure"]) / 4)
        return result

    except Exception as e:
        print(f"LLM error: {e}")
        return {
            "scores": {"empathy": 70, "articulation": 70, "grammar": 70, "structure": 70},
            "overall": 70,
            "hinglish_corrections": [],
            "tips": ["Practice speaking clearly", "Use structured answers", "Reduce filler words"],
        }