import importlib.util, json, os, pathlib, struct, subprocess, tempfile, unittest
spec=importlib.util.spec_from_file_location('host', str(pathlib.Path(__file__).resolve().parents[1]/'host.py'))
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
class HostTests(unittest.TestCase):
 def test_plain_text(self):
  d=h.validate({'notes':[{'id':'abc-12','title':'<img src="https://invalid/">','text':'<b>hello</b>'}]})
  self.assertEqual(d['notes'][0]['text'],'<b>hello</b>')
 def test_validation(self):
  for data in ({'notes':[{'id':'../../x','title':'a','text':'b'}]}, {'notes':[],'accountPath':'https://evil/'}, {'notes':[],'accountPath':3}, {'notes':[{}]}, {'notes':[{}]*201}):
   with self.assertRaises(ValueError): h.validate(data)
 def test_protocol_and_permissions(self):
  with tempfile.TemporaryDirectory() as tmp:
   data=json.dumps({'notes':[{'id':'test','title':'Pin','text':'Body'}],'accountPath':'/u/1/'}).encode()
   out=subprocess.check_output(['python3',str(pathlib.Path(__file__).resolve().parents[1]/'host.py')],input=struct.pack('<I',len(data))+data,env={**os.environ,'XDG_CACHE_HOME':tmp})
   self.assertTrue(json.loads(out[4:])['ok'])
   p=pathlib.Path(tmp)/'omarchy-keep-pins/notes.json'
   self.assertEqual(p.stat().st_mode&0o777,0o600)
   self.assertEqual(p.parent.stat().st_mode&0o777,0o700)
   self.assertEqual(json.loads(p.read_text())['accountPath'],'/u/1/')
 def test_large_protocol(self):
  out=subprocess.check_output(['python3',str(pathlib.Path(__file__).resolve().parents[1]/'host.py')],input=struct.pack('<I',h.LIMIT+1))
  self.assertFalse(json.loads(out[4:])['ok'])
unittest.main()
