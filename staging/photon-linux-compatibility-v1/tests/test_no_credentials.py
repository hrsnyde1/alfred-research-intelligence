import os,socket,unittest
class IsolationTests(unittest.TestCase):
    def test_no_provider_credentials_in_environment(self):
        self.assertFalse(any('SECRET' in k or 'TOKEN' in k or k.startswith('PHOTON') for k in os.environ))
    def test_network_denied_and_owner_credentials_unreadable(self):
        with self.assertRaises(OSError):
            with socket.socket() as s:s.settimeout(1);s.connect(('127.0.0.1',9))
        with self.assertRaises(PermissionError):
            os.listdir('/Users/haydensnyder')
