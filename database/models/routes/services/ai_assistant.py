
from config import Config


SYSTEM_PROMPT = """
You are the DigitalSentinel digital risk protection assistant.

Help users understand brand impersonation, suspicious profiles,
app listings, risk indicators, and safe incident response.

Use simple, practical language.
Do not claim that a profile is fraudulent without sufficient evidence.
Explain that similarity and heuristic risk scores are indicators,
not proof. Never invent live platform verification.
"""


def ask_ai(message):
    message = str(message or "").strip()

    if not message:
        return {
            "success": False,
            "reply": "Please enter a question."
        }

    if len(message) > 4000:
        return {
            "success": False,
            "reply": "Your message is too long."
        }

    if not Config.GROQ_API_KEY:
        return {
            "success": False,
            "reply": (
                "The AI assistant is not configured. "
                "Add GROQ_API_KEY to your .env file."
            )
        }

    try:
        from groq import Groq

        client = Groq(api_key=Config.GROQ_API_KEY)

        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=700
        )

        answer = response.choices[0].message.content or (
            "No answer was returned. Please try again."
        )

        return {
            "success": True,
            "reply": answer
        }

    except Exception:
        # Keep API keys and provider error details out of user responses.
        return {
            "success": False,
            "reply": (
                "The AI service is unavailable. Check your API "
                "configuration and try again."
            )
        }
