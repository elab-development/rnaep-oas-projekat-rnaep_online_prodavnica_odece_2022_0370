import unittest
from unittest.mock import patch, AsyncMock
import database
# Uvozimo repozitorijum (ne treba nam više u testu, ali ga ostavljamo zbog strukture)
import repository

# Patchujemo 'get_db' u database modulu da bi sprečili bilo kakvu konekciju
with patch('database.get_db', return_value=AsyncMock()):
    from search.service import SearchService

class TestSearchServiceIntegration(unittest.IsolatedAsyncioTestCase):
    
    # Ovde patchujemo ProductRepository unutar search modula
    @patch('search.service.ProductRepository')
    async def test_search_with_repo_integration(self, mock_repo_class):
        # 1. Priprema: Mockujemo repozitorijum da ne pokušava da se poveže na bazu
        mock_repo = mock_repo_class.return_value
        mock_repo.search = AsyncMock(return_value=[{"name": "Test Proizvod"}])
        
        # 2. Inicijalizacija servisa
        service = SearchService()
        
        # 3. Akcija: Pozivamo servis
        # Sada ovo neće stići do prave baze jer je repo mockovan
        result = await service.search(q="test", category=None, collection=None, min_price=None, max_price=None)
        
        # 4. Provera
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test Proizvod")
        mock_repo.search.assert_called_once()

if __name__ == '__main__':
    unittest.main()