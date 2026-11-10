// Refresh only while Keep is open. Never fetch or modify Google data ourselves.
let previous = '', timer, active = false;
async function sync() {
  if (active) return;
  const payload = extractPinned(document, location);
  if (!payload) return;
  const snapshot = JSON.stringify(payload);
  if (snapshot === previous) return;
  active = true;
  try {
    const result = await chrome.runtime.sendMessage({type:'keep-pins', payload});
    if (result?.ok) previous = snapshot;
  } catch (_) { /* Retried on the next interval; no note content is logged. */ }
  finally { active = false; }
}
new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(sync, 1500); })
  .observe(document.body, {subtree:true, childList:true, attributes:true, characterData:true});
setInterval(() => { previous = ''; sync(); }, 60000);
window.addEventListener('hashchange', () => setTimeout(sync, 1500));
sync();
