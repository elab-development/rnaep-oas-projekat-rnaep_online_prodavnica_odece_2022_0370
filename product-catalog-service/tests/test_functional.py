import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import database

# 1. Patchujemo bazu pre importa glavne aplikacije
# Ovo osigurava da aplikacija ne pokuša da se poveže na MongoDB
with patch('database.get_db', return_value=AsyncMock()):
    from main import app 

client = TestClient(app)

class TestSearchFunctional(unittest.TestCase):

    @patch('search.service.SearchService.search')
    def test_search_endpoint_success(self, mock_search):
        # Simuliramo uspešan odgovor servisa
        mock_search.return_value = [{"id": "1", "name": "Majica"}]
        
        # 2. Pozivamo endpoint koji smo videli u ruti (/products/search)
        response = client.get("/products/search?q=majica")
        
        # 3. Proveravamo rezultat
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Majica")
        
        # Proveravamo da li je servis pozvan
        mock_search.assert_called_once()

    def test_health_check(self):
        # Dodatni mali test da potvrdimo da aplikacija radi
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

if __name__ == '__main__':
    unittest.main()