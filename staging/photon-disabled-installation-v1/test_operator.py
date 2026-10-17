import importlib.util,json,os,pathlib,tempfile,unittest
spec=importlib.util.spec_from_file_location('operator_candidate',pathlib.Path(__file__).with_name('operator.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
HERE=pathlib.Path(__file__).parent
BASE=HERE.parent/'photon-two-project-v1/baseline'
class OperatorTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=pathlib.Path(self.temp.name)/'root';self.root.mkdir()
  self.backup=pathlib.Path(self.temp.name)/'backup';plan=json.loads((HERE/'INSTALL_MANIFEST.json').read_text());self.records=plan['records'];self.guards=plan['guards']
  for r in self.records:
   for k in ('old_uid','old_gid','new_uid','new_gid'):r[k]=os.getuid() if k.endswith('uid') else os.getgid()
   if r['old']:
    p=self.root/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
    rel=r['path'].split('/hermes-agent/')[1];p.write_bytes((BASE/rel).read_bytes());p.chmod(r['old_mode'])
  for g in self.guards:
   p=self.root/g['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((BASE/g['path'].split('/hermes-agent/')[1]).read_bytes())
  self.state=self.root/'var/lib/alfredphoton/delivery-fixture';self.state.parent.mkdir(parents=True);self.state.write_bytes(b'synthetic sent receipt and retry history')
  self.before=self.snapshot()
 def snapshot(self):return {str(p.relative_to(self.root)):(p.read_bytes(),m.metadata(p)) for p in self.root.rglob('*') if p.is_file()}
 def install(self,hook=lambda n:None):m.apply(self.root,HERE,self.backup,self.records,self.guards,hook)
 def test_exact_install_and_rollback_preserve_records_metadata_and_disable_config(self):
  self.install()
  for r in self.records:self.assertEqual(m.digest((self.root/r['path']).read_bytes()),r['new'])
  self.assertEqual(self.state.read_bytes(),b'synthetic sent receipt and retry history')
  for r in self.records:
   if r['path'].endswith('.conf'):self.assertEqual((self.root/r['path']).read_bytes(),b'[Service]\nEnvironment=PHOTON_RESEARCH_ENABLED=0\n')
  m.rollback(self.root,self.backup);self.assertEqual(self.snapshot(),self.before)
 def test_partial_installation_restores_all_original_files(self):
  def fail(n):
   if n==3:raise RuntimeError('synthetic interruption')
  with self.assertRaises(RuntimeError):self.install(fail)
  m.rollback(self.root,self.backup);self.assertEqual(self.snapshot(),self.before)
 def test_baseline_drift_rejected_before_writes(self):
  r=next(r for r in self.records if r['old']);(self.root/r['path']).write_bytes(b'unknown')
  before=self.snapshot()
  with self.assertRaises(ValueError):self.install()
  self.assertEqual(self.snapshot(),before);self.assertFalse(self.backup.exists())
 def test_unexpected_new_target_rejected(self):
  r=next(r for r in self.records if r['old'] is None);p=self.root/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'unknown')
  with self.assertRaises(ValueError):self.install()
  self.assertFalse(self.backup.exists())
 def test_rollback_refuses_unknown_code_without_touching_any_file(self):
  self.install();r=self.records[-1];(self.root/r['path']).write_bytes(b'unknown')
  before=self.snapshot()
  with self.assertRaises(ValueError):m.rollback(self.root,self.backup)
  self.assertEqual(self.snapshot(),before)
 def test_rollback_refuses_corrupted_backup(self):
  self.install();i=next(i for i,r in enumerate(self.records) if r['old']);(self.backup/str(i)).write_bytes(b'bad')
  before=self.snapshot()
  with self.assertRaises(ValueError):m.rollback(self.root,self.backup)
  self.assertEqual(self.snapshot(),before)
 def test_symlink_target_rejected(self):
  r=next(r for r in self.records if r['old'] is None);p=self.root/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(self.state)
  with self.assertRaises(ValueError):self.install()
  self.assertEqual(self.state.read_bytes(),b'synthetic sent receipt and retry history')
 def test_artifact_hash_drift_rejected(self):
  self.records[0]['new']='0'*64
  with self.assertRaises(ValueError):self.install()
  self.assertEqual(self.snapshot(),self.before)
 def test_extended_attributes_preserved_across_install_and_rollback(self):
  r=next(r for r in self.records if r['old']);p=self.root/r['path']
  key='user.alfred_review' if hasattr(os,'setxattr') else 'com.alfred.review'
  m.write_attr(p,key,b'synthetic metadata');before=self.snapshot()
  self.install();self.assertEqual(m.read_attrs(p)[key],b'synthetic metadata')
  m.rollback(self.root,self.backup);self.assertEqual(self.snapshot(),before)
