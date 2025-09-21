const chatEl = document.getElementById('chat');
const promptEl = document.getElementById('prompt');
const sendBtn = document.getElementById('send');

function appendMessage(text, cls) {
  const d = document.createElement('div');
  d.className = 'msg ' + cls;
  d.textContent = text;
  chatEl.appendChild(d);
  chatEl.scrollTop = chatEl.scrollHeight;
}

sendBtn.addEventListener('click', async () => {
  const prompt = promptEl.value.trim();
  if (!prompt) return;
  appendMessage(prompt, 'user');
  promptEl.value = '';
  appendMessage('Memproses...', 'bot');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();

    // Hapus "Memproses..." terakhir
    const bots = Array.from(document.querySelectorAll('.bot'));
    const lastBot = bots[bots.length - 1];
    if (lastBot && lastBot.textContent === 'Memproses...') lastBot.remove();

    if (res.ok && data.reply) appendMessage(data.reply, 'bot');
    else appendMessage('Error: ' + (data.error || 'Tidak diketahui'), 'bot');
  } catch (err) {
    appendMessage('Koneksi error: ' + err.message, 'bot');
  }
});
