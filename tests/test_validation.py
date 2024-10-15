import unittest
from src.main import app

class ValidationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test for missing 'aula' parameter
    def test_missing_aula_parameter(self):
        response = self.app.get('/lessons?edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"loc":["aula"]', response.data)  # Updated assertion for missing 'aula'

    # Test for missing 'edificio' parameter
    def test_missing_edificio_parameter(self):
        response = self.app.get('/lessons?aula=6144b62e06477900174b0cfd')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"loc":["edificio"]', response.data)  # Updated assertion for missing 'edificio'

    # Test for invalid 'aula' length
    def test_invalid_aula_length(self):
        response = self.app.get('/lessons?aula=123456789012345678901234567890123&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'String should have at most 30 characters', response.data)

    # Test for invalid 'aula' format
    def test_invalid_aula_format(self):
        response = self.app.get('/lessons?aula=invalid!aula&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"String should match pattern", response.data)

if __name__ == '__main__':
    unittest.main()
