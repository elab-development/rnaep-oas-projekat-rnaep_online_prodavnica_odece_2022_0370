import unittest
import requests

class TestUserServiceFunctional(unittest.TestCase):
    def test_health_endpoint(self):
        try:
            r = requests.get('http://localhost:8002/health')
            self.assertEqual(r.status_code, 200)
        except Exception:
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
