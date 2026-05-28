import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mockujemo sve zavisnosti rute pre importa main-a
with patch('database.get_db', return_value=MagicMock()):
    # Pretpostavka da je app u main.py
    from main import app 

client = TestClient(app)

class TestProductServiceFunctional(unittest.TestCase):
    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

if __name__ == '__main__':
    unittest.main()