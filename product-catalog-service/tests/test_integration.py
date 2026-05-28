import unittest
import sqlite3

class TestProductServiceIntegration(unittest.TestCase):
    def test_db_connection(self):
        try:
            conn = sqlite3.connect(':memory:')
            self.assertIsNotNone(conn)
        finally:
            conn.close()

if __name__ == '__main__':
    unittest.main()
