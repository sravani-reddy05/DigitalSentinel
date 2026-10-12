// static/js/assistant.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");

    if (form) {
        form.addEventListener("submit", sendChatMessage);
    }

    document.querySelectorAll(".prompt-btn").forEach((button) => {
        button.addEventListener("click", () => {
            if (input) {
                input.value = button.textContent.trim();
                input.focus();
            }
        });
    });
});

async function sendChatMessage(event) {
    event.preventDefault();

    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");
    const button = document.getElementById("sendButton");

    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    const waiting = addMessage("Thinking…", "assistant");
    button.disabled = true;

    try {
        const response = await fetch("/api/assistant/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Assistant request failed.");
        }

        waiting.textContent =
            result.response || result.answer || result.message ||
            "The assistant did not return a response.";
    } catch (error) {
        waiting.textContent = `Unable to get a response: ${error.message}`;
    } finally {
        button.disabled = false;
        input.focus();
        messages.scrollTop = messages.scrollHeight;
    }
}

function addMessage(text, type) {
    const messages = document.getElementById("chatMessages");
    const bubble = document.createElement("div");

    bubble.className = type === "user"
        ? "chat-bubble user-bubble"
        : "chat-bubble assistant-bubble";

    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;

    return bubble;
}