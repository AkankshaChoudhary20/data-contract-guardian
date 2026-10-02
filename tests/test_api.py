import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from guardian import api
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();api.DB=str(Path(self.tmp.name)/'test.db');self.client=TestClient(api.app)
    def tearDown(self):self.tmp.cleanup()
    def test_versioned_flow(self):
        body={'name':'orders','schema':{'fields':{'id':{'type':'integer'}}}}
        first=self.client.post('/api/contracts',json=body).json();second=self.client.post('/api/contracts',json=body).json()
        self.assertEqual(second['version'],2)
        result=self.client.post('/api/validate',json={'contract_id':first['id'],'content':'[{"id":1}]','format':'json'})
        self.assertTrue(result.json()['valid'])
        self.assertFalse(self.client.post('/api/compare',json={'old_id':first['id'],'new_id':second['id']}).json()['breaking'])
        self.assertEqual(len(self.client.get('/api/contracts').json()),2)
    def test_invalid_schema_and_missing_contract(self):
        self.assertEqual(self.client.post('/api/contracts',json={'name':'x','schema':{}}).status_code,400)
        self.assertEqual(self.client.post('/api/validate',json={'contract_id':999,'content':'[]'}).status_code,404)
if __name__=='__main__':unittest.main()
