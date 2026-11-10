#!/usr/bin/python3
"""Chromium native messaging receiver. No sockets, credentials, or cloud service."""
import json
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
import time

LIMIT = 3_000_000

def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get('notes'), list) or len(data['notes']) > 200:
        raise ValueError('Invalid notes')
    account = data.get('accountPath', '/')
    if not isinstance(account, str) or not re.fullmatch(r'/(?:u/\d+/)?', account):
        raise ValueError('Invalid account')
    notes, seen = [], set()
    for note in data['notes']:
        if not isinstance(note, dict):
            raise ValueError('Invalid note')
        ident, title, body = (note.get(k) for k in ('id', 'title', 'text'))
        if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,160}', ident) or ident in seen:
            raise ValueError('Invalid identifier')
        if not isinstance(title, str) or len(title) > 500 or not isinstance(body, str) or len(body) > 12000:
            raise ValueError('Invalid text')
        seen.add(ident)
        notes.append({'id': ident, 'title': title, 'text': body})
    result = {'notes': notes, 'accountPath': account, 'updated': int(time.time())}
    diagnostic = data.get('diagnostics')
    names = ('dataId', 'unpin', 'pin', 'unpinCapital', 'pressedPins', 'noteCards', 'titles', 'bodies', 'listItems', 'dialogs', 'navigation', 'requested', 'matched', 'clicked', 'noteOpen')
    if isinstance(diagnostic, dict):
        result['diagnostics'] = {name: diagnostic[name] for name in names
                                 if type(diagnostic.get(name)) is int and 0 <= diagnostic[name] <= 10000}
    if isinstance(diagnostic, dict) and isinstance(diagnostic.get('structure'), list):
        structure = []
        for card in diagnostic['structure'][:2]:
            if not isinstance(card, list): continue
            nodes = []
            for node in card[:65]:
                if not isinstance(node, dict): continue
                nodes.append({key: node[key][:500] for key in ('tag','attributes','classes','role','pinLabel','pinTooltip')
                              if isinstance(node.get(key), str)})
            structure.append(nodes)
        result.setdefault('diagnostics', {})['structure'] = structure
    return result

def save(data, filename="notes.json"):
    folder = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'omarchy-keep-pins'
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    fd, name = tempfile.mkstemp(dir=folder)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream)
        os.replace(name, folder/filename)
    finally:
        if os.path.exists(name): os.unlink(name)

def main():
    try:
        header = sys.stdin.buffer.read(4)
        if len(header) != 4: return
        length, = struct.unpack('<I', header)
        if length > LIMIT: raise ValueError('Message too large')
        raw = sys.stdin.buffer.read(length)
        if len(raw) != length: raise ValueError('Incomplete message')
        incoming = json.loads(raw)
        if isinstance(incoming, dict) and incoming.get('diagnosticsOnly') is True:
            checked = validate({'notes': [], 'diagnostics': incoming.get('diagnostics')})
            save({'diagnostics': checked.get('diagnostics', {}), 'updated': checked['updated']}, 'navigation.json' if checked.get('diagnostics', {}).get('navigation') == 1 else 'diagnostics.json')
        else:
            save(validate(incoming))
        reply = {'ok': True}
    except (ValueError, OSError, TypeError):
        reply = {'ok': False}
    encoded = json.dumps(reply).encode()
    sys.stdout.buffer.write(struct.pack('<I', len(encoded)) + encoded)
    sys.stdout.buffer.flush()

if __name__ == '__main__': main()
