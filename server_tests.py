import os
import server
import unittest
import tempfile
import AutomationConfig

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        if os.path.exists('test.config'):
            os.remove('test.config')
        AutomationConfig.SetConfigFilename('test.config')
        AutomationConfig.Read()
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def test_empty_config(self):
        rv = self.app.get('/automation/controllers')
        assert 'No Controllers defined' in rv.data
        rv = self.app.get('/automation/actuators')
        assert 'No Actuators defined' in rv.data
        rv = self.app.get('/automation/aliases')
        assert 'No Aliases defined' in rv.data
        rv = self.app.get('/automation/config')
        assert 'No Config defined' in rv.data

    def test_add_controller():

if __name__ == '__main__':
    unittest.main()

