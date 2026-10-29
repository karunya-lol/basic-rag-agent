/**
 * NoteWise — Clean Frontend Controller (static/app.js)
 */

const chatContainer = document.getElementById('chat-container');
const chatFeed = document.getElementById('chat-feed');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const hero = document.getElementById('hero');
const apiKeyInput = document.getElementById('api-key');

const fileInput = document.getElementById('file-input');
const uploadTrigger = document.getElementById('upload-trigger');
const uploadStatus = document.getElementById('upload-status');
const docList = document.getElementById('doc-list');
const docCount = document.getElementById('doc-count');
const clearBtn = document.getElementById('clear-btn');

// File Upload Trigger
uploadTrigger.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
  if (!e.target.files.length) return;
  const file = e.target.files[0];

  uploadStatus.textContent = `Uploading ${file.name}...`;
  uploadTrigger.disabled = true;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (data.status === 'success') {
      uploadStatus.textContent = `✓ Indexed ${file.name}`;
      setTimeout(() => { uploadStatus.textContent = ''; }, 3000);
      loadDocs();
    } else {
      uploadStatus.textContent = `Upload failed: ${data.message || ''}`;
    }
  } catch (err) {
    uploadStatus.textContent = `Error: ${err.message}`;
  } finally {
    uploadTrigger.disabled = false;
    fileInput.value = '';
  }
});

// Load Ingested Documents
async function loadDocs() {
  try {
    const res = await fetch('/api/docs');
    const data = await res.json();
    if (data.status === 'success' && data.documents) {
      docCount.textContent = data.documents.length;
      if (data.documents.length === 0) {
        docList.innerHTML = `<div style="font-size: 0.75rem; color: var(--text-dim);">No notes uploaded.</div>`;
        return;
      }
      docList.innerHTML = data.documents.map(d => `
        <div class="doc-item">
          <span>📄</span>
          <span class="name" title="${escapeHtml(d.filename)}">${escapeHtml(d.filename)}</span>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error(e);
  }
}

// Clear all data
clearBtn.addEventListener('click', async () => {
  if (confirm("Clear all notes and conversation history?")) {
    await fetch('/api/reset', { method: 'POST' });
    chatContainer.innerHTML = '';
    if (hero) chatContainer.appendChild(hero);
    loadDocs();
  }
});

// Click prompt chip
function ask(text) {
  chatInput.value = text;
  handleSubmit(new Event('submit'));
}

// Handle chat query
async function handleSubmit(e) {
  if (e) e.preventDefault();
  const query = chatInput.value.trim();
  if (!query) return;

  if (hero && hero.parentNode) {
    hero.remove();
  }

  // Append user bubble
  appendMessage('user', query);
  chatInput.value = '';
  chatInput.disabled = true;
  sendBtn.disabled = true;

  // Append loading
  const loadingId = 'loading-' + Date.now();
  appendLoading(loadingId);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: query,
        api_key: apiKeyInput.value.trim()
      })
    });
    const data = await res.json();
    removeLoading(loadingId);

    if (data.status === 'success') {
      appendMessage('assistant', data.answer, data.sources);
    } else {
      appendMessage('assistant', `⚠️ **Error**: ${data.message || 'Failed to generate answer'}`);
    }
  } catch (err) {
    removeLoading(loadingId);
    appendMessage('assistant', `⚠️ **Network Error**: ${err.message}`);
  } finally {
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

function appendMessage(role, content, sources = []) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = role === 'assistant' ? marked.parse(content) : escapeHtml(content);
  msg.appendChild(bubble);

  // Sources
  if (sources && sources.length > 0) {
    const sourcesBox = document.createElement('div');
    sourcesBox.className = 'sources';

    const toggle = document.createElement('div');
    toggle.className = 'sources-toggle';
    toggle.innerHTML = `<span>Sources (${sources.length})</span><span>▾</span>`;

    const list = document.createElement('div');
    list.className = 'sources-list';
    list.innerHTML = sources.map((s, idx) => `
      <div class="source-entry">
        <strong>${escapeHtml(s.source)} (Page ${s.page})</strong><br>
        "${escapeHtml(s.text)}"
      </div>
    `).join('');

    toggle.addEventListener('click', () => {
      list.classList.toggle('open');
    });

    sourcesBox.appendChild(toggle);
    sourcesBox.appendChild(list);
    msg.appendChild(sourcesBox);
  }

  chatContainer.appendChild(msg);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

function appendLoading(id) {
  const msg = document.createElement('div');
  msg.className = 'message assistant';
  msg.id = id;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = `<span style="color: var(--text-dim); font-style: italic;">Searching notes...</span>`;
  msg.appendChild(bubble);

  chatContainer.appendChild(msg);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

function removeLoading(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Initial document fetch
loadDocs();
