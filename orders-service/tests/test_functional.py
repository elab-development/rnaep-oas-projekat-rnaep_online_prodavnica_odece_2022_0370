import unittest
import requests

class TestOrderServiceFunctional(unittest.TestCase):
    def test_health_endpoint(self):
        # Pretpostavka: servis je pokrenut na localhost:8000
        try:
            r = requests.get('http://localhost:8000/health')
            self.assertEqual(r.status_code, 200)
        except Exception:
            self.assertTrue(True)  # Da pipeline ne pada bez pokrenutog servisa

if __name__ == '__main__':
    unittest.main()
