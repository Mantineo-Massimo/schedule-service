import unittest
from src.main import app

class ErrorHandlingTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test for unexpected server error (500 response)
    def test_unexpected_error(self):
        with self.assertRaises(Exception):
            response = self.app.get('/lessons?aula=error&edificio=5f6cb2c183c80e0018f4d470')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"An unexpected error occurred", response.data)


if __name__ == '__main__':
    unittest.main()
