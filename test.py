import unittest
from fastapi.testclient import TestClient

from main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_user(self):
        payload = {
            "name": "John Doe",
            "email": "johndoe@example.com"
        }

        response = self.client.post('/api/users', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
        self.assertEqual(response.json()['name'], "John Doe")
        self.assertEqual(response.json()['email'], "johndoe@example.com")

    def test_get_user(self):
        user_id = 1

        response = self.client.get(f'/api/user/{user_id}')

        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
        self.assertEqual(response.json()['id'], user_id)

    def test_delete_user(self):
        user_id = 1

        response = self.client.delete(f'/api/user/{user_id}')

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], "User deleted successfully")


if __name__ == '__main__':
    unittest.main()
