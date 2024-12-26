import unittest

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMain(unittest.TestCase):
    def test_health_check(self):
        response = client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
