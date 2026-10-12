
def get_voice_response(message, language="en"):
    message = str(message or "").strip()

    if not message:
        return {
            "reply": "Please say or type a question."
        }

    text = message.lower()

    language = language.split("-")[0].lower()
    if language == "hi":
        reply = "जोखिम स्कोर संकेतों पर आधारित है, धोखाधड़ी का प्रमाण नहीं। URL जांच केवल तभी लाइव होगी जब VirusTotal या Google Safe Browsing कॉन्फ़िगर हो।"
    elif language == "es":
        reply = "La puntuación de riesgo es un indicador, no una prueba de fraude. La comprobación URL solo es en vivo si VirusTotal o Google Safe Browsing están configurados."
    elif language == "fr":
        reply = "Le score de risque est un indicateur, pas une preuve de fraude. La vérification URL est réelle uniquement si VirusTotal ou Google Safe Browsing est configuré."
    elif language == "de":
        reply = "Der Risikowert ist ein Hinweis, kein Betrugsbeweis. Eine echte URL-Prüfung ist nur mit konfiguriertem VirusTotal oder Google Safe Browsing verfügbar."
    elif language == "te":
        reply = "రిస్క్ స్కోర్ ఒక సూచిక మాత్రమే; మోసానికి రుజువు కాదు. VirusTotal లేదా Google Safe Browsing కాన్ఫిగర్ చేసినప్పుడే URL తనిఖీ నిజమైన ఫలితాన్ని ఇస్తుంది."
    elif "risk score" in text or "risk level" in text:
        reply = (
            "The risk score is a heuristic indicator based on "
            "selected signals. A high score requires human review "
            "and is not proof of fraud."
        )

    elif "impersonation" in text or "fake account" in text:
        reply = (
            "Check the username, account history, official links, "
            "publisher information, and any suspicious requests. "
            "Do not rely on name similarity alone."
        )

    elif "report" in text:
        reply = (
            "Open the Reports page to review recorded detections "
            "and export a CSV summary."
        )

    else:
        reply = (
            "I can help explain risk scores, brand impersonation, "
            "detections, and reports. Please ask a more specific question."
        )

    return {"reply": reply}
