import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from database import get_db

# 1. Kreiramo mock za bazu
mock_db = MagicMock()

# 2. Dependency Override - FastAPI sada koristi naš mock
app.dependency_overrides[get_db] = lambda: mock_db

client = TestClient(app)

class TestOrdersFunctional(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "orders-service")

    def test_get_orders_empty(self):
        # Primer kako testirati endpoint koji bi vratio 404 (npr. nema narudžbina)
        # Ovdje bi mogla dodati mock logiku za OrderRepository ako treba
        pass

if __name__ == '__main__':
    unittest.main()