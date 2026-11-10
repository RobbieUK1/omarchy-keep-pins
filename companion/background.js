chrome.action.onClicked.addListener(() => chrome.tabs.create({url: 'https://keep.google.com/'}));
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (!sender.tab || !sender.url?.startsWith('https://keep.google.com/') || message?.type !== 'keep-pins') return;
  chrome.runtime.sendNativeMessage('org.omarchy.keep_pins', message.payload, reply => {
    const error = chrome.runtime.lastError;
    chrome.action.setBadgeText({text: error ? '!' : ''});
    chrome.action.setBadgeBackgroundColor({color: '#b45309'});
    respond({ok: !error && reply?.ok === true});
  });
  return true;
});
