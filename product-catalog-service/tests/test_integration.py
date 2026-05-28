import unittest
from unittest.mock import patch, MagicMock

# Patchujemo bazu da ne pokušava konekciju
with patch('repository.get_db', return_value=MagicMock()):
    from repository import ProductRepository

class TestProductServiceIntegration(unittest.TestCase):
    def test_db_connection(self):
        # Testiramo da li repozitorijum radi sa mockovanom bazom
        repo = ProductRepository()
        self.assertIsNotNone(repo.db)

if __name__ == '__main__':
    unittest.main()