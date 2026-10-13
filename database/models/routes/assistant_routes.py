
from flask import Blueprint, request, jsonify, render_template
from flask import current_app
import os

from config import Config

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/assistant")
def assistant_page():
    return render_template("assistant.html")


@assistant_bp.route("/api/assistant/chat", methods=["POST"])
def assistant_chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    language = str(data.get("language", "en"))[:12].lower()
    if language not in {"en", "hi", "te"}:
        language = "en"
    history = data.get("history", [])
    if not isinstance(history, list):
        return jsonify({"error": "Chat history must be a list"}), 400
    if any(
        not isinstance(item, dict)
        or item.get("role") not in {"user", "assistant"}
        or not isinstance(item.get("content"), str)
        for item in history
    ):
        return jsonify({"error": "Chat history contains an invalid message"}), 400
    history = [
        {"role": item["role"], "content": item["content"][:4000]}
        for item in history[-8:]
        if item["content"].strip()
    ]

    if not message:
        return jsonify({"error": "Please enter a message"}), 400

    if len(message) > 4000:
        return jsonify({"error": "Message is too long"}), 400

    groq_key = os.getenv("GROQ_API_KEY", "").strip() or Config.GROQ_API_KEY.strip()
    if not groq_key:
        from database.models.routes.services.voice_assistant import get_voice_response
        return jsonify({
            "reply": get_voice_response(message, language=language, history=history)["reply"],
            "mode": "local_fallback",
            "language": language
        }), 200

    try:
        from groq import Groq

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are DigitalSentinel's digital risk "
                        "protection assistant. Explain brand "
                        "impersonation, suspicious usernames, "
                        "risk scores, app listings, and safe "
                        "incident response in simple language. "
                        "Never claim that a profile is fraudulent without sufficient evidence. Similarity scores are indicators, not proof. Answer in the user's language when possible. The user's preferred language is " + language + "."
                    )
                },
                *history,
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=700
        )

        reply = response.choices[0].message.content or (
            "I couldn't generate a response. Please try again."
        )

        return jsonify({
            "reply": reply,
            "mode": "groq_ai",
            "language": language
        })

    except Exception:
        current_app.logger.exception("Groq assistant request failed")
        from database.models.routes.services.voice_assistant import get_voice_response
        fallback = get_voice_response(message, language=language, history=history)
        return jsonify({
            "reply": fallback["reply"],
            "mode": "local_fallback",
            "language": language
        }), 200
