
document.addEventListener("DOMContentLoaded", function () {
    const voiceButton = document.getElementById("voiceButton");
    const speakReplyButton = document.getElementById("speakReplyButton");
    const chatInput = document.getElementById("chatInput");
    const voiceLanguage = document.getElementById("voiceLanguage");

    // Voice input: speak and convert speech to text
    if (voiceButton) {
        voiceButton.addEventListener("click", function () {
            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                window.showAlert ? window.showAlert("Voice input is not supported in this browser. You can type your question instead.", "warning") : alert("Voice input is not supported in this browser. You can type your question instead.");
                return;
            }

            const recognition = new SpeechRecognition();
            recognition.lang = voiceLanguage ? voiceLanguage.value : "en-US";
            recognition.interimResults = false;
            recognition.continuous = false;

            voiceButton.disabled = true;
            voiceButton.innerHTML = '<i class="bi bi-mic-fill"></i> Listening…';

            recognition.onresult = function (event) {
                const transcript =
                    event.results[0][0].transcript;

                if (chatInput) {
                    chatInput.value = transcript;
                    window.voiceReplyRequested = true;
                    const chatForm = document.getElementById("chatForm");
                    if (chatForm && chatForm.requestSubmit) {
                        chatForm.requestSubmit();
                    } else if (chatForm) {
                        chatForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
                    }
                }
            };

            recognition.onerror = function (event) {
                console.error("Speech recognition error:", event.error);
                window.showAlert ? window.showAlert("Voice input failed: " + event.error, "warning") : alert("Voice input failed: " + event.error);
            };

            recognition.onend = function () {
                voiceButton.disabled = false;
                voiceButton.innerHTML = '<i class="bi bi-mic"></i>';
            };

            try {
                recognition.start();
            } catch (error) {
                console.error("Could not start voice recognition:", error);
                voiceButton.disabled = false;
                voiceButton.textContent = "Speak";
            }
        });
    }

    // Read the latest assistant response aloud
    if (speakReplyButton) {
        speakReplyButton.addEventListener("click", function () {
            if (!("speechSynthesis" in window)) {
                alert("Text-to-speech is not supported in this browser.");
                return;
            }

            const replies =
                document.querySelectorAll(".assistant-bubble");

            if (replies.length === 0) {
                alert("There is no assistant reply to read yet.");
                return;
            }

            const lastReply = replies[replies.length - 1];
            const text = lastReply.textContent.trim();

            if (!text) {
                alert("The latest assistant reply is empty.");
                return;
            }

            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = voiceLanguage ? voiceLanguage.value : "en-US";
            utterance.rate = 1;

            window.speechSynthesis.speak(utterance);
        });
    }
});
