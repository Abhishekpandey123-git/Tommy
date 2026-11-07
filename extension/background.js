const API = 'http://localhost:8000/api/explain';

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'explain-selection',
    title: 'Explain with AI Reading Assistant',
    contexts: ['selection']
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'explain-selection' || !tab?.id || !info.selectionText) return;
  try {
    const settings = await chrome.storage.local.get({ language: 'hi', level: 'beginner' });
    const response = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: info.selectionText, language: settings.language, level: settings.level })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    await chrome.tabs.sendMessage(tab.id, { type: 'show-explanation', data });
  } catch (error) {
    await chrome.tabs.sendMessage(tab.id, { type: 'show-error', message: error.message });
  }
});
