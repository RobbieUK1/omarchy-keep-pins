import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class InstallTests(unittest.TestCase):
    def test_install_and_upgrade_preserve_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary)/'config'
            shell = config/'omarchy/shell.json'
            shell.parent.mkdir(parents=True)
            original = {'version':1,'idle':{'lock':900},'bar':{'layout':{'left':[{'id':'test.clock'}],'right':[{'id':'test.audio'}]}}}
            shell.write_text(json.dumps(original))
            env = {**os.environ, 'XDG_CONFIG_HOME':str(config)}
            for _ in range(2):
                subprocess.run(['python3',str(ROOT/'install.py')],check=True,env=env,stdout=subprocess.DEVNULL)
            actual = json.loads(shell.read_text())
            self.assertEqual(actual['idle'], original['idle'])
            self.assertEqual(actual['bar']['layout']['left'], original['bar']['layout']['left'])
            self.assertEqual(actual['bar']['layout']['right'],[{'id':'robbie.keep-pins'},{'id':'test.audio'}])
            native = json.loads((config/'chromium/NativeMessagingHosts/org.omarchy.keep_pins.json').read_text())
            self.assertEqual(native['allowed_origins'],['chrome-extension://'+(ROOT/'extension-id.txt').read_text().strip()+'/'])
            self.assertTrue(os.access(native['path'],os.X_OK))
            target = config/'omarchy/plugins/robbie.keep-pins'
            self.assertTrue((target/'companion/manifest.json').exists())
            self.assertFalse((target/'.git').exists())
            self.assertFalse((target/'__pycache__').exists())
            self.assertEqual(len(list((config/'omarchy/plugin-backups').iterdir())),1)

    def test_bad_configuration_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary)
            shell = config/'omarchy/shell.json'
            shell.parent.mkdir()
            shell.write_text('{broken')
            result = subprocess.run(['python3',str(ROOT/'install.py')],env={**os.environ,'XDG_CONFIG_HOME':str(config)},capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(shell.read_text(),'{broken')
            self.assertFalse((config/'omarchy/plugins/robbie.keep-pins').exists())

if __name__ == '__main__': unittest.main()
