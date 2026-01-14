let currentUser = null;

async function register() {
    const username = document.getElementById('username').value;
    if (!username) return alert("Please enter a username");

    const response = await fetch(`/register?username=${encodeURIComponent(username)}`, {
        method: 'POST'
    });

    currentUser = await response.json();
    document.getElementById('user-info').innerText = `Logged in as: ${currentUser.username} (ID: ${currentUser.id})`;
    addMessage('ai', `Welcome back, ${currentUser.username}! Your personal knowledge base is ready.`);
}

const dropzone = document.getElementById('upload-dropzone');
const fileInput = document.getElementById('file-input');

dropzone.onclick = () => fileInput.click();

fileInput.onchange = async (e) => {
    if (!currentUser) return alert("Please login first");
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const statusDiv = document.getElementById('file-status');
    statusDiv.innerText = "Uploading and processing... ⏳";
    statusDiv.style.color = "var(--primary)";

    try {
        const response = await fetch(`/upload?user_id=${currentUser.id}`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        const successMsg = `✅ Document "${file.name}" processed into ${result.chunks} chunks.`;
        statusDiv.innerText = successMsg;
        statusDiv.style.color = "var(--success)";

        // Also notify in chat
        addMessage('ai', successMsg);
    } catch (err) {
        statusDiv.innerText = "❌ Error processing document.";
        statusDiv.style.color = "#f85149";
    }
};

async function sendQuery() {
    if (!currentUser) return alert("Please login first");
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value;
    if (!query) return;

    addMessage('user', query);
    queryInput.value = '';

    // Add loading indicator
    const history = document.getElementById('chat-history');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message loading';
    loadingDiv.innerText = 'Thinking... 🔍';
    history.appendChild(loadingDiv);
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch(`/query?user_id=${currentUser.id}&q=${encodeURIComponent(query)}`);
        const result = await response.json();

        // Remove loading indicator
        history.removeChild(loadingDiv);

        addMessage('ai', result.answer, result.sources);
    } catch (err) {
        history.removeChild(loadingDiv);
        addMessage('ai', "❌ Sorry, I encountered an error while processing your request.");
    }
}

function addMessage(role, text, sources = []) {
    const history = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;

    let content = text;
    if (sources && sources.length > 0) {
        content += `<br><br><small style="color: var(--text-muted)">Sources: ${[...new Set(sources)].join(', ')}</small>`;
    }

    msgDiv.innerHTML = content;
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
}

// Enter key support
document.getElementById('query-input').onkeypress = (e) => {
    if (e.key === 'Enter') sendQuery();
};
