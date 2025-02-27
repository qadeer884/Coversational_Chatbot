let conversation = [];
let currentChatId = null;

// Load history when page loads
window.onload = loadChatHistory;

document.getElementById("submit").addEventListener("click", sendMessage);
document.getElementById("prompt").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function addChatBubble(message, sender) {
    const chatContainer = document.querySelector(".chat-container");
    const chatBox = document.createElement("div");
    chatBox.classList.add(sender === "user" ? "user-chat-box" : "ai-chat-box");
    chatBox.innerHTML = `<div class="${sender === 'user' ? 'user-chat-area' : 'ai-chat-area'}">${message}</div>`;
    chatContainer.appendChild(chatBox);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const promptInput = document.getElementById("prompt");
    const userMessage = promptInput.value.trim();
    if (userMessage === "") return;

    addChatBubble(userMessage, "user");
    conversation.push({ role: "user", content: userMessage });
    promptInput.value = "";

    fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation: conversation, chat_id: currentChatId }),
    })
        .then((response) => response.json())
        .then((data) => {
            addChatBubble(data.response, "ai");
            conversation.push({ role: "ai", content: data.response });
            currentChatId = data.chat_id; // Keep using the same chat ID
            saveChatHistory();
        })
        .catch((error) => {
            console.error("Error:", error);
            addChatBubble("❌ Failed to get response.", "ai");
        });
}

function loadChatHistory() {
    fetch("/get_history").then(res => res.json()).then((history) => {
        const historyList = document.getElementById("historyList");
        historyList.innerHTML = "";
        history.forEach(chat => {
            const div = document.createElement("div");
            div.className = "chat-history";
            div.textContent = chat.title;
            div.onclick = () => loadChat(chat.id);
            historyList.appendChild(div);
        });
    });
}

function loadChat(chatId) {
    fetch(`/get_chat/${chatId}`).then(res => res.json()).then((data) => {
        currentChatId = chatId;
        conversation = data.conversation;
        const chatContainer = document.getElementById("chatContainer");
        chatContainer.innerHTML = "";
        conversation.forEach(msg => addChatBubble(msg.content, msg.role));
    });
}

function startNewChat() {
    currentChatId = null;
    conversation = [];
    document.getElementById("chatContainer").innerHTML = `<div class="ai-chat-box"><div class="ai-chat-area">Hello! How can I assist you today?</div></div>`;
}

function saveChatHistory() {
    fetch("/save_history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation, chat_id: currentChatId }),
    }).then(loadChatHistory);
}
