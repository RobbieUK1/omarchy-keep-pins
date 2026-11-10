// Shared by synchronization and direct-note navigation, so local IDs agree.
function readKeepCard(card) {
  const titleNode = card.querySelector('.vIzZGf-r4nke-YPqjbf, .IZ65Hb-r4nke, [role="heading"]');
  const bodyNode = card.querySelector('.IZ65Hb-vIzZGf-bVEB4e-qJTHM, .IZ65Hb-qJTHM-haAclf, .bN97Pc');
  const title = (titleNode?.innerText || titleNode?.textContent || '').trim().slice(0,500);
  const text = (bodyNode?.innerText || bodyNode?.textContent || '').trim().slice(0,12000);
  let id = card.getAttribute('data-id');
  if (!id || !/^[A-Za-z0-9._-]{1,160}$/.test(id)) {
    // Current Keep cards have no public ID. Use a stable local identity;
    // the desktop opens these through Keep search instead of a fake note URL.
    let hash = 2166136261;
    for (const character of title + '\n' + text) hash = Math.imul(hash ^ character.codePointAt(0), 16777619) >>> 0;
    id = 'local_' + hash.toString(16);
  }
  return {id, title, text};
}

// Main Notes page only: label/search/archive views are partial snapshots.
function extractPinned(doc, location) {
  if (!/^#?(?:home)?$/.test(location.hash) || doc.querySelector('[role="dialog"]')) return null;
  const cards = [...doc.querySelectorAll('.IZ65Hb-n0tgWb, [data-id]')];
  const notes = [], seen = new Set();
  for (const card of cards) {
    const pin = card.querySelector('[aria-label="Unpin"], [aria-label="Unpin note"], [data-tooltip-text="Unpin"], [data-tooltip="Unpin note"], .nQ1Faf[aria-pressed="true"], .VYMape[aria-pressed="true"]');
    if (!pin) continue;
    const {id, title, text} = readKeepCard(card);
    if (seen.has(id)) continue;
    seen.add(id);
    notes.push({id, title, text});
    if (notes.length >= 200) break;
  }
  const ready = doc.querySelector('.IZ65Hb-n0tgWb, [aria-label="Take a note…"], [aria-label="Take a note..."]');
  return ready ? {notes, accountPath: /^\/u\/\d+\/$/.test(location.pathname) ? location.pathname : '/'} : null;
}
if (typeof module !== 'undefined') module.exports = {extractPinned, readKeepCard};

function keepDiagnostics(doc) {
  const count = selector => Math.min(doc.querySelectorAll(selector).length, 10000);
  return {
    structure: [...doc.querySelectorAll('.IZ65Hb-n0tgWb')].slice(0, 2).map(card =>
      [card, ...card.querySelectorAll('*')].slice(0, 65).map(el => ({
        tag: el.tagName,
        attributes: [...el.attributes].map(a => a.name).join(' ').slice(0, 500),
        classes: String(el.className).slice(0, 300),
        role: (el.getAttribute('role') || '').slice(0, 60),
        pinLabel: /pin/i.test(el.getAttribute('aria-label') || '') ? (el.getAttribute('aria-label') || '').slice(0, 80) : '',
        pinTooltip: /pin/i.test(el.getAttribute('data-tooltip') || '') ? (el.getAttribute('data-tooltip') || '').slice(0, 80) : ''
      }))),
    dataId: count('[data-id]'),
    unpin: count('[aria-label="Unpin note"], [data-tooltip="Unpin note"]'),
    pin: count('[aria-label="Pin note"], [data-tooltip="Pin note"]'),
    unpinCapital: count('[aria-label="Unpin Note"], [data-tooltip="Unpin Note"]'),
    pressedPins: count('.VYMape[aria-pressed="true"]'),
    noteCards: count('.IZ65Hb-n0tgWb'),
    titles: count('.IZ65Hb-r4nke'),
    bodies: count('.IZ65Hb-YPqjbf'),
    listItems: count('[role="listitem"]'),
    dialogs: count('[role="dialog"]')
  };
}
