import unittest
from data_extractor import app

class LessonsAPITestCase(unittest.TestCase):

    def setUp(self):
        # Set up a test client
        self.app = app.test_client()
        self.app.testing = True  # Enable testing mode

    def test_missing_parameters(self):
        # Test the API when no parameters are provided
        response = self.app.get('/lessons')
        self.assertEqual(response.status_code, 400)

        # Adjust the assertion to check for the updated error message
        self.assertIn(b"Input should be a valid string", response.data)

    def test_valid_request(self):
        # Test the API with valid 'aula' and 'edificio' parameters (replace with valid values)
        response = self.app.get('/lessons?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"start_time", response.data)
        self.assertIn(b"end_time", response.data)

    def test_invalid_parameter_length(self):
        # Test with invalid parameter lengths
        response = self.app.get('/lessons?aula=123456789012345678901234567890123&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response.status_code, 400)

        # Adjust the assertion to check for the updated error message
        self.assertIn(b'String should have at most 30 characters', response.data)

if __name__ == '__main__':
    unittest.main()
