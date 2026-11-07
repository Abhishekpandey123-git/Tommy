(() => {
  let panel = null;

  function removePanel() {
    if (panel) panel.remove();
    panel = null;
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  }

  function render(data) {
    removePanel();
    panel = document.createElement('div');
    panel.className = 'ara-panel';
    panel.innerHTML = `
      <div class="ara-header">
        <span>AI Reading Assistant</span>
        <button class="ara-close" aria-label="Close">×</button>
      </div>
      <div class="ara-body">
        <div class="ara-section"><div class="ara-label">🧠 Simple English</div><div>${escapeHtml(data.simple_english)}</div></div>
        <div class="ara-section"><div class="ara-label">🇮🇳 Hindi</div><div>${escapeHtml(data.hindi)}</div></div>
        ${data.difficult_words?.length ? `<div class="ara-section"><div class="ara-label">📖 Difficult words</div><ul>${data.difficult_words.map(w => `<li><b>${escapeHtml(w.word)}</b> — ${escapeHtml(w.meaning)}${w.example ? `<br><small>${escapeHtml(w.example)}</small>` : ''}</li>`).join('')}</ul></div>` : ''}
        ${data.example ? `<div class="ara-section"><div class="ara-label">💡 Example</div><div>${escapeHtml(data.example)}</div></div>` : ''}
        ${data.confusion_reason ? `<div class="ara-section"><div class="ara-label">🔎 Why it may feel confusing</div><div>${escapeHtml(data.confusion_reason)}</div></div>` : ''}
      </div>`;
    document.body.appendChild(panel);
    panel.querySelector('.ara-close').onclick = removePanel;
    const rect = window.getSelection()?.getRangeAt(0)?.getBoundingClientRect();
    panel.style.top = `${Math.min((rect?.bottom ?? 80) + window.scrollY + 8, window.scrollY + window.innerHeight - 420)}px`;
    panel.style.left = `${Math.min((rect?.left ?? 20) + window.scrollX, window.scrollX + window.innerWidth - 390)}px`;
  }

  function showError(message) {
    render({ simple_english: `Could not explain the selection: ${message}`, hindi: 'कृपया सुनिश्चित करें कि local backend चल रहा है।' });
  }

  chrome.runtime.onMessage.addListener(message => {
    if (message.type === 'show-explanation') render(message.data);
    if (message.type === 'show-error') showError(message.message);
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') removePanel();
  });
})();
