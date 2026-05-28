import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import database
import repository 

# Patchujemo bazu pre nego što uvezemo servis da izbegnemo konekciju
with patch('database.get_db', return_value=MagicMock()):
    from search.service import SearchService

class TestSearchServiceUnit(unittest.IsolatedAsyncioTestCase):
    
    # Patchujemo repozitorijum direktno tamo gde ga servis koristi
    @patch('search.service.ProductRepository')
    async def test_search_logic(self, mock_repo_class):
        # 1. Priprema
        mock_repo = mock_repo_class.return_value
        # Simuliramo da repozitorijum vraća listu proizvoda
        mock_repo.search = AsyncMock(return_value=[{"id": "1", "name": "Majica"}])
        
        service = SearchService()
        
        # 2. Akcija
        # Pozivamo search sa parametrima koje tvoja funkcija očekuje
        result = await service.search(
            q="majica", 
            category=None, 
            collection=None, 
            min_price=10, 
            max_price=50
        )
        
        # 3. Provera
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Majica")
        
        # Proveravamo da li je repozitorijum pozvan sa ispravnim query-jem
        mock_repo.search.assert_called_once()
        
        # Dobijamo pozvani argument (query)
        call_args = mock_repo.search.call_args[0][0]
        self.assertIn("price", call_args)
        self.assertEqual(call_args["price"]["$gte"], 10)

if __name__ == '__main__':
    unittest.main()