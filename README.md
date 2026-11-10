# 💡 Keep Pins for Omarchy

A yellow light bulb in your bar opens a native, theme-aware dropdown of pinned Google Keep notes. **Open Keep ↗** launches `omarchy launch webapp` so Keep has its own app window. Clicking a note opens it in a web app window too. Up/Down selects a note; Enter opens it; Escape closes the dropdown.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/RobbieUK1/omarchy-keep-pins/v1.2.0/install.sh | bash
```

Run this as your normal desktop user, without sudo. Requires Omarchy with the Quickshell plugin system, Chromium, Python 3, curl and tar. The installer downloads the tagged release and includes the Chromium companion. To inspect the installer first, [read install.sh](install.sh). From a downloaded checkout, you can also run `python3 install.py`. The installer backs up an existing plugin and shell configuration, installs the widget and Chromium native messaging registration, and adds the widget to the right of the bar. No Python packages are required.

Then follow **Set up sync** in the dropdown: load `~/.config/omarchy/plugins/robbie.keep-pins/companion` as an unpacked extension at `chrome://extensions`, and open/reload Keep in the same Chromium profile. The Google sign-in stays in your browser. Keep the main Notes page open for synchronization.

## Chromium companion

- [Download the companion extension ZIP](https://github.com/RobbieUK1/omarchy-keep-pins/releases/download/v1.2.0/keep-pins-chromium-v1.2.0.zip)
- [Browse the extension source](companion)
- [Detailed setup guide](https://github.com/RobbieUK1/omarchy-keep-pins/blob/main/SETUP.html)

The one-line installer already puts the companion in the correct permanent folder. In Chromium:

1. Open `chrome://extensions` and enable **Developer mode**.
2. Choose **Load unpacked** and select `~/.config/omarchy/plugins/robbie.keep-pins/companion` (Ctrl+L lets you enter a full path).
3. Click the yellow bulb, then **Open Keep ↗**. Sign in yourself if needed, and reload an existing Keep window once.
4. Keep the main **Notes** page open for syncing.

The ZIP is an alternative download: extract it into a permanent folder before using **Load unpacked**. Install the desktop plugin as well, since the companion needs its local receiver. This release is available from GitHub; it is not published in the Chrome Web Store. Browser enablement is a separate manual step, following [Chromium's unpacked extension workflow](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked).

## How it works and limitations

The companion reads pinned cards from the signed-in Keep page; no API tokens, passwords, remote relay, remote code or cloud service are involved. It uses only nativeMessaging permission and a content script restricted to https://keep.google.com/. The receiver accepts this extension ID only, validates messages and atomically writes private cache files (directory mode 0700, file mode 0600). The plugin displays note text as plain text, including markup-shaped content. All notes are read-only here; edit in Keep.

Checks occur on page changes and every 60 seconds while Keep is open. Disable/remove the companion in Chromium to stop synchronization. The local widget continues to show the last snapshot and indicates when it is older than two minutes. There is no background Google polling without an open Keep page. Cache location: `${XDG_CACHE_HOME:-~/.cache}/omarchy-keep-pins/notes.json`.

This is a browser-page integration, not an official Google Keep API client. Google may change its DOM. English accessible pin labels are supported, with current CSS hooks as a fallback. Search, label, archive views and active note dialogs are ignored. A cache is not replaced until the main Notes page is recognized. This version targets Chromium, one Google account at a time, text previews only, up to 200 pinned notes. If multiple accounts are open, the last one to sync wins.

Automated tests cover message validation, private cache writes, markup handling and extension extraction logic using fixtures. Live synchronization and individual-note navigation were verified with the user on the current Keep layout.

## Updating

Run the installer again. It preserves the existing bar position, backs up the previous installation outside the active plugins folder, and moves legacy duplicate Keep Pins backups out of that folder. Reload **Omarchy Keep Pins** at `chrome://extensions`, then refresh Keep. If the bar still shows an older version after updating, run `omarchy restart shell`.

## Opening individual notes

Keep does not expose public IDs on every note card. Where an ID is available, the widget uses its direct note URL. Otherwise it opens a Keep app window with a local navigation marker; the companion matches the pinned card and opens it automatically. Keep the companion enabled in the same Chromium profile. This does not edit the note or fall back to an all-notes search.

Local diagnostics contain page structure and navigation counts, without note contents. They are stored beside the notes cache as `diagnostics.json` and `navigation.json`. No diagnostic data is uploaded by the plugin.

## Development checks

```bash
python3 tests/test_host.py
python3 tests/test_install.py
node tests/test-extract.cjs
omarchy plugin validate .
```

## Remove

Remove the companion from Chromium. Run `omarchy plugin disable robbie.keep-pins`, then remove `~/.config/omarchy/plugins/robbie.keep-pins`, `~/.config/chromium/NativeMessagingHosts/org.omarchy.keep_pins.json`, and the cache directory above. Installer backups are left in place.

MIT license. No affiliation with Google.
