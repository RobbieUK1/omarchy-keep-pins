#!/usr/bin/python3
"""Install the bar widget and Chromium local receiver for the current user."""
import hashlib
import base64
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time


def install():
    source = Path(__file__).resolve().parent
    config = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config'))).resolve()
    target = config/'omarchy/plugins/robbie.keep-pins'
    shell = config/'omarchy/shell.json'
    # Validate inputs before touching the installed plugin or desktop layout.
    settings = json.loads(shell.read_text()) if shell.exists() else {'version': 1}
    if not isinstance(settings, dict):
        raise ValueError('Expected an object in shell.json')
    bar = settings.setdefault('bar', {})
    layout = bar.setdefault('layout', {})
    if not isinstance(layout, dict) or not isinstance(layout.get('right', []), list):
        raise ValueError('Invalid bar layout in shell.json')
    extid = (source/'extension-id.txt').read_text().strip()
    extension = json.loads((source/'companion/manifest.json').read_text())
    digest = hashlib.sha256(base64.b64decode(extension['key'], validate=True)).hexdigest()[:32]
    expected = ''.join(chr(97 + int(c, 16)) for c in digest)
    if not re.fullmatch('[a-p]{32}', extid) or extid != expected:
        raise ValueError('The companion ID does not match its public key')
    stamp = str(time.time_ns())
    # Legacy installers created backups beside active plugins. Their duplicate
    # manifests can override the working widget, so move them out of discovery.
    if target.parent.exists():
        for candidate in target.parent.iterdir():
            if candidate == target or not candidate.is_dir(): continue
            try:
                manifest = json.loads((candidate/'manifest.json').read_text())
            except (OSError, ValueError):
                continue
            if isinstance(manifest, dict) and manifest.get('id') == 'robbie.keep-pins':
                backup = config/'omarchy/plugin-backups'/(candidate.name + '-legacy-' + stamp)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(candidate), str(backup))
    if source != target:
        if target.exists():
            backup = config/'omarchy/plugin-backups'/('robbie.keep-pins-' + stamp)
            shutil.copytree(target, backup, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        shutil.copytree(source, target, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    os.chmod(target/'host.py', 0o755)
    host = {'name':'org.omarchy.keep_pins','description':'Omarchy Keep Pins local receiver',
            'path':str(target/'host.py'),'type':'stdio',
            'allowed_origins':['chrome-extension://' + extid + '/']}
    folder = config/'chromium/NativeMessagingHosts'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/'org.omarchy.keep_pins.json'
    if path.exists():
        shutil.copy2(path, path.with_suffix('.json.bak-' + stamp))
    temporary = path.with_suffix('.json.tmp-' + stamp)
    temporary.write_text(json.dumps(host, indent=2) + '\n')
    temporary.replace(path)
    present = any((item.get('id') if isinstance(item, dict) else item) == 'robbie.keep-pins'
                  for section in layout.values() if isinstance(section, list) for item in section)
    if not present:
        layout.setdefault('right', []).insert(0, {'id': 'robbie.keep-pins'})
        if shell.exists():
            shutil.copy2(shell, shell.with_suffix('.json.bak-' + stamp))
        temporary = shell.with_suffix('.json.tmp-' + stamp)
        temporary.write_text(json.dumps(settings, indent=2) + '\n')
        temporary.replace(shell)
    print('Installed Keep Pins: look for the yellow light bulb in your bar.')
    print('One-time Chromium setup: chrome://extensions > Developer mode > Load unpacked')
    print('Choose this folder: ' + str(target/'companion'))
    print('After updating: reload Omarchy Keep Pins at chrome://extensions and refresh Keep.')
    print('If the bar retains the old version: omarchy restart shell')
    print('Then use Open Keep in the dropdown and reload Keep if it was already open.')


if __name__ == '__main__':
    try:
        install()
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as error:
        print('Keep Pins installation failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
