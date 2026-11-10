// Use Keep's accessible pin controls, with current CSS hooks as a fallback.
// Only the main notes route is authoritative; search/labels/archive are partial views.
function extractPinned(doc, location) {
  if (!/^#?(?:home)?$/.test(location.hash) || doc.querySelector('[role="dialog"]')) return null;
  const cards = [...doc.querySelectorAll('[data-id]')].filter(el =>
    el.querySelector('[aria-label="Unpin note"], [data-tooltip="Unpin note"], .VYMape[aria-pressed="true"]'));
  const seen = new Set();
  const notes = [];
  for (const card of cards) {
    const id = card.getAttribute('data-id');
    if (!/^[A-Za-z0-9._-]{1,160}$/.test(id) || seen.has(id)) continue;
    seen.add(id);
    const title = card.querySelector('.IZ65Hb-r4nke, [role="heading"]')?.textContent || '';
    const body = card.querySelector('.IZ65Hb-YPqjbf, .bN97Pc')?.textContent || '';
    notes.push({id, title: title.slice(0,500), text: body.slice(0,12000)});
    if (notes.length === 200) break;
  }
  // Do not erase the cache while Keep is loading or if the markup changes.
  const ready = doc.querySelector('.IZ65Hb-n0tgWb, [aria-label="Take a note…"], [aria-label="Take a note..."]');
  return ready ? {notes, accountPath: /^\/u\/\d+\/$/.test(location.pathname) ? location.pathname : '/'} : null;
}
if (typeof module !== 'undefined') module.exports = {extractPinned};
