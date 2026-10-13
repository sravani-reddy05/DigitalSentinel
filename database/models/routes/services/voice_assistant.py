def get_voice_response(message, language="en", history=None):
    message = str(message or "").strip()
    if not message:
        return {"reply": "Please say or type a question."}

    text = message.casefold()
    language = str(language or "en").split("-")[0].lower()
    if language not in {"en", "hi", "te"}:
        language = "en"

    intents = {
        "greeting": (
            ("hello", "hi ", "hey", "good morning", "good afternoon", "नमस्ते", "हेलो", "హలో", "నమస్కారం"),
            {
                "en": "Hello! I can help you understand risk findings, suspicious accounts, app listings, and safe review steps. What would you like to know?",
                "hi": "नमस्ते! मैं जोखिम के संकेत, संदिग्ध खातों, ऐप लिस्टिंग और सुरक्षित समीक्षा के बारे में मदद कर सकता हूँ। आप क्या जानना चाहते हैं?",
                "te": "నమస్కారం! రిస్క్ సూచనలు, అనుమానాస్పద ఖాతాలు, యాప్ లిస్టింగ్‌లు, సురక్షిత సమీక్ష గురించి నేను సహాయం చేయగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
            },
        ),
        "risk": (
            ("risk", "score", "severity", "जोखिम", "स्कोर", "రిస్క్", "స్కోర్", "ప్రమాద స్థాయి"),
            {
                "en": "A risk score summarizes signals such as name similarity, account details, and suspicious links. Treat it as a review priority, not proof of fraud. Check each signal and compare it with the brand's verified information.",
                "hi": "जोखिम स्कोर नाम की समानता, खाते के विवरण और संदिग्ध लिंक जैसे संकेतों का सार है। इसे समीक्षा की प्राथमिकता मानें, धोखाधड़ी का प्रमाण नहीं। हर संकेत को जाँचें और ब्रांड की सत्यापित जानकारी से तुलना करें।",
                "te": "రిస్క్ స్కోర్ పేరు పోలిక, ఖాతా వివరాలు, అనుమానాస్పద లింక్‌ల వంటి సూచనలను సంక్షిప్తంగా చూపిస్తుంది. దీన్ని సమీక్ష ప్రాధాన్యతగా చూడండి; మోసానికి రుజువుగా కాదు. ప్రతి సూచనను బ్రాండ్ ధృవీకరించిన సమాచారంతో పోల్చండి.",
            },
        ),
        "impersonation": (
            ("impersonat", "fake account", "fake profile", "copycat", "नकली खाता", "नकली प्रोफ़ाइल", "नकल", "నకిలీ ఖాతా", "నకిలీ ప్రొఫైల్", "అనుకరణ"),
            {
                "en": "To review a possible impersonation, compare the exact username, account history, official links, contact details, and any requests for money or credentials. Name similarity alone is not enough to confirm a fake account.",
                "hi": "संभावित नकली खाते की समीक्षा के लिए उपयोगकर्ता नाम, खाते का इतिहास, आधिकारिक लिंक, संपर्क विवरण और पैसे या पासवर्ड माँगने वाली बातों की तुलना करें। केवल नाम की समानता नकली खाते की पुष्टि नहीं करती।",
                "te": "అనుకరణ ఖాతాను సమీక్షించేటప్పుడు ఖచ్చితమైన యూజర్‌నేమ్, ఖాతా చరిత్ర, అధికారిక లింక్‌లు, సంప్రదింపు వివరాలు, డబ్బు లేదా పాస్‌వర్డ్ అడిగే అభ్యర్థనలను పరిశీలించండి. పేరు పోలిక ఒక్కటే నకిలీ ఖాతాను నిర్ధారించదు.",
            },
        ),
        "url": (
            ("url", "link", "website", "phishing", "लिंक", "वेबसाइट", "यूआरएल", "లింక్", "వెబ్‌సైట్", "యూఆర్ఎల్"),
            {
                "en": "Check that the domain spelling and destination are expected before opening a link. A live reputation result is available only when a URL reputation provider is configured; otherwise, treat the link as unverified.",
                "hi": "लिंक खोलने से पहले डोमेन की वर्तनी और गंतव्य जाँचें। लाइव प्रतिष्ठा परिणाम तभी उपलब्ध है जब URL सुरक्षा सेवा कॉन्फ़िगर हो; अन्यथा लिंक को असत्यापित मानें।",
                "te": "లింక్‌ను తెరవడానికి ముందు డొమైన్ స్పెల్లింగ్ మరియు గమ్యస్థానాన్ని పరిశీలించండి. URL భద్రతా సేవ కాన్ఫిగర్ చేసినప్పుడే ప్రత్యక్ష ప్రతిష్ఠ ఫలితం అందుతుంది; లేకపోతే ఆ లింక్‌ను ధృవీకరించనిదిగా పరిగణించండి.",
            },
        ),
        "review": (
            ("review", "detection", "investigate", "check", "समीक्षा", "जांच", "जाँच", "पहचान", "పరిశీలన", "సమీక్ష", "డిటెక్షన్", "తనిఖీ"),
            {
                "en": "Review a detection by checking its evidence, source, risk reasons, and the brand's verified assets. Record a decision only after comparing multiple signals, and mark uncertain cases for human follow-up.",
                "hi": "किसी जोखिम की समीक्षा में उसके प्रमाण, स्रोत, जोखिम के कारण और ब्रांड की सत्यापित संपत्तियाँ जाँचें। कई संकेतों की तुलना के बाद ही निर्णय दर्ज करें; अनिश्चित मामलों को आगे मानवीय समीक्षा के लिए भेजें।",
                "te": "డిటెక్షన్‌ను సమీక్షించేటప్పుడు ఆధారాలు, మూలం, రిస్క్ కారణాలు, బ్రాండ్ ధృవీకరించిన ఆస్తులను పరిశీలించండి. అనేక సూచనలను పోల్చిన తర్వాతే నిర్ణయం నమోదు చేయండి; అనిశ్చిత సందర్భాలను మానవ సమీక్షకు పంపండి.",
            },
        ),
        "report": (
            ("report", "export", "रिपोर्ट", "निर्यात", "నివేదిక", "ఎగుమతి"),
            {
                "en": "Open Reports to review recorded detections and export a CSV summary. Use the dashboard for high-level trends and the detection list for individual case details.",
                "hi": "दर्ज जोखिम देखने और CSV सारांश निर्यात करने के लिए रिपोर्ट पृष्ठ खोलें। समग्र रुझानों के लिए डैशबोर्ड और प्रत्येक मामले के विवरण के लिए जोखिम सूची देखें।",
                "te": "నమోదైన డిటెక్షన్‌లను పరిశీలించి CSV సారాంశాన్ని ఎగుమతి చేయడానికి Reports పేజీని తెరవండి. మొత్తం ధోరణుల కోసం డ్యాష్‌బోర్డ్‌ను, ఒక్కో కేసు వివరాల కోసం డిటెక్షన్‌ల జాబితాను చూడండి.",
            },
        ),
        "app": (
            ("app", "application", "publisher", "developer", "ऐप", "एप्लिकेशन", "प्रकाशक", "डेवलपर", "యాప్", "అప్లికేషన్", "ప్రచురణకర్త", "డెవలపర్"),
            {
                "en": "When reviewing an app listing, compare the publisher, official store link, app name, permissions, and description with the brand's verified details. A similar name by itself does not establish that an app is malicious.",
                "hi": "ऐप लिस्टिंग की समीक्षा करते समय प्रकाशक, आधिकारिक स्टोर लिंक, ऐप का नाम, अनुमतियाँ और विवरण ब्रांड की सत्यापित जानकारी से मिलाएँ। केवल मिलता-जुलता नाम यह साबित नहीं करता कि ऐप दुर्भावनापूर्ण है।",
                "te": "యాప్ లిస్టింగ్‌ను సమీక్షించేటప్పుడు ప్రచురణకర్త, అధికారిక స్టోర్ లింక్, యాప్ పేరు, అనుమతులు, వివరణలను బ్రాండ్ ధృవీకరించిన వివరాలతో పోల్చండి. పేరు పోలిక ఒక్కటే యాప్ హానికరమని నిరూపించదు.",
            },
        ),
    }

    for _, (keywords, localized_replies) in intents.items():
        if any(keyword in text for keyword in keywords):
            return {"reply": localized_replies[language]}

    if history:
        if language == "hi":
            reply = "मैं आपकी पिछली बात के संदर्भ में मदद करना चाहता हूँ। कृपया बताएं कि आप किस जोखिम, खाते, लिंक या समीक्षा के बारे में पूछ रहे हैं।"
        elif language == "te":
            reply = "మీ ముందరి సందేశం ఆధారంగా సహాయం చేయగలను. మీరు ఏ రిస్క్, ఖాతా, లింక్ లేదా సమీక్ష గురించి అడుగుతున్నారో కొంచెం వివరించండి."
        else:
            reply = "I can help with that. Could you share which risk finding, account, link, or review you mean?"
    elif language == "hi":
        reply = "मैं DigitalSentinel के जोखिम स्कोर, संदिग्ध खातों, लिंक, ऐप लिस्टिंग और समीक्षा में मदद कर सकता हूँ। अपने सवाल का थोड़ा और विवरण दें।"
    elif language == "te":
        reply = "DigitalSentinel రిస్క్ స్కోర్‌లు, అనుమానాస్పద ఖాతాలు, లింక్‌లు, యాప్ లిస్టింగ్‌లు, సమీక్షల గురించి నేను సహాయం చేయగలను. మీ ప్రశ్నను కొంచెం వివరించండి."
    else:
        reply = "I can help with DigitalSentinel risk scores, suspicious accounts, links, app listings, and reviews. Tell me a little more about what you're looking at."

    return {"reply": reply}
