const language = document.querySelector('#language');
const level = document.querySelector('#level');
const status = document.querySelector('#status');
chrome.storage.local.get({ language: 'hi', level: 'beginner' }).then(s => { language.value = s.language; level.value = s.level; });
async function save() {
  await chrome.storage.local.set({ language: language.value, level: level.value });
  status.textContent = 'Settings saved.';
  setTimeout(() => status.textContent = '', 1200);
}
language.onchange = save; level.onchange = save;
