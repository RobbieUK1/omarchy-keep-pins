window.keepPinsNavigation = {navigation:1, requested: new URL(location.href).searchParams.has('omarchyNote') ? 1 : 0, matched:0, clicked:0, noteOpen:0};
// Refresh only while Keep is open. Never fetch or modify Google data ourselves.
let previous = '', timer, active = false;
async function sync() {
  if (active) return;
  try {
    await chrome.runtime.sendMessage({type:'keep-pins', payload:{diagnosticsOnly:true, diagnostics:keepDiagnostics(document)}});
  } catch (_) {}
  if (window.keepPinsNavigation.requested) {
    try { await chrome.runtime.sendMessage({type:'keep-pins', payload:{diagnosticsOnly:true, diagnostics:window.keepPinsNavigation}}); } catch (_) {}
  }
  const payload = extractPinned(document, location);
  if (!payload) return;
  payload.diagnostics = keepDiagnostics(document);
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

// An app-window link may target a local card ID when Keep exposes no note ID.
// Resolve it against the rendered pinned cards, then let Keep open the card.
// No note text is entered, changed, or sent to another service.
const requestedNote = new URL(location.href).searchParams.get('omarchyNote');
if (requestedNote && /^local_[a-f0-9]{1,8}$/.test(requestedNote)) {
  let attempts = 0, clicked = false;
  const navigationTimer = setInterval(() => {
    if (++attempts > 90) { clearInterval(navigationTimer); return; }
    if (/^#NOTE\//i.test(location.hash)) {
      window.keepPinsNavigation.noteOpen = 1;
      sync();
      const clean = new URL(location.href);
      clean.searchParams.delete('omarchyNote');
      history.replaceState(history.state, '', clean.href);
      clearInterval(navigationTimer);
      return;
    }
    if (clicked || document.querySelector('[role="dialog"]')) return;
    for (const card of document.querySelectorAll('.IZ65Hb-n0tgWb, [data-id]')) {
      if (readKeepCard(card).id !== requestedNote) continue;
      window.keepPinsNavigation.matched = 1;
      clicked = true;
      // Use the card's non-editing content region; never activate toolbar controls.
      const target = card.querySelector('.IZ65Hb-r4nke-haAclf') || card;
      target.click();
      window.keepPinsNavigation.clicked = 1;
      sync();
      break;
    }
  }, 500);
}
