import unittest
from src.main import app
from src.models import cache

class CacheHandlingTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        cache.clear()  # Clear the cache before each test

    # Test cache functionality with valid request
    def test_cache_valid_request(self):
        response_1 = self.app.get('/lessons?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response_1.status_code, 200)

        # Make the request again and it should hit the cache
        response_2 = self.app.get('/lessons?aula=6144b62e06477900174b0cfd&edificio=5f6cb2c183c80e0018f4d470')
        self.assertEqual(response_2.status_code, 200)


if __name__ == '__main__':
    unittest.main()
