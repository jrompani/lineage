const isLocalhost = window.location.hostname === '127.0.0.1';
const protocol = isLocalhost ? 'ws://' : 'wss://';
const chatSocket = new WebSocket(
    protocol + window.location.host + '/ws/chat/' + groupName + '/'
);    

chatSocket.onerror = function(e) {
    console.error('WebSocket error:', e);
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    appendMessage(data.message, data.sender, data.avatar_url, data.sender === currentUser);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();

document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    if (message.trim()) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender': currentUser
        }));
        appendMessage(message, currentUser, currentUserAvatar, true);
        messageInputDom.value = '';
    }
};

function appendMessage(message, sender, avatarUrl, isSent) {
    const messagesContainer = document.getElementById('messages-container');
    const chatLog = document.getElementById('chat-log');

    const timestamp = new Date().toLocaleString([], { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: false
    });
    
    const senderName = sender;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', isSent ? 'sent' : 'received');

    messageDiv.innerHTML = `
        <img src="${avatarUrl}" class="message-avatar" alt="${senderName}" width="40" height="40">
        <div class="message-content">
            <div class="message-header">
                <strong class="sender-name">${senderName}</strong>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-text">${message}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.querySelector('#chat-message-input');
    const emojiButton = document.querySelector('#emoji-button');
    
    // Inicialize o Emoji Button
    const picker = new EmojiButton();

    // Mostra o seletor de emojis ao clicar no botão
    emojiButton.addEventListener('click', () => {
        picker.togglePicker(emojiButton);
    });

    // Insere o emoji no campo de texto quando selecionado
    picker.on('emoji', emoji => {
        chatInput.value += emoji;
        chatInput.focus(); // Foca no campo de texto após inserir o emoji
    });

    const chatLog = document.getElementById('chat-log');
    chatLog.scrollTop = chatLog.scrollHeight;
});
