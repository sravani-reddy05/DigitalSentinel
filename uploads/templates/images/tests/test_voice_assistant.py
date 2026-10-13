from database.models.routes.services.voice_assistant import get_voice_response


def test_local_assistant_gives_different_answers_for_different_questions():
    risk_reply = get_voice_response("What does this risk score mean?", "en")
    report_reply = get_voice_response("How do I export a report?", "en")

    assert risk_reply["reply"] != report_reply["reply"]
    assert "not proof of fraud" in risk_reply["reply"]
    assert "CSV" in report_reply["reply"]


def test_local_assistant_responds_in_selected_supported_languages():
    hindi_reply = get_voice_response("मेरे जोखिम स्कोर का क्या अर्थ है?", "hi")
    telugu_reply = get_voice_response("రిస్క్ స్కోర్ అంటే ఏమిటి?", "te")
    english_reply = get_voice_response("What is an app listing?", "en")

    assert "जोखिम स्कोर" in hindi_reply["reply"]
    assert "రిస్క్ స్కోర్" in telugu_reply["reply"]
    assert "app listing" in english_reply["reply"]


def test_unsupported_languages_fall_back_to_english():
    response = get_voice_response("What is a risk score?", "fr")

    assert "risk score" in response["reply"]
