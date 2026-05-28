import unittest
from unittest.mock import patch, MagicMock

# Patchujemo bazu pre importa servisa
with patch('database.get_db', return_value=MagicMock()):
    from products.service import ProductService

class TestProductServiceUnit(unittest.TestCase):
    @patch('products.service.ProductRepository')
    def test_create_product(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        service = ProductService()
        
        # Simuliramo uspešno kreiranje
        mock_repo.create.return_value = {"id": "123", "name": "Test"}
        
        self.assertTrue(True) # Ovde bi dodao aserte na result

if __name__ == '__main__':
    unittest.main()