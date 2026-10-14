import unittest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

class TestErrorHandling(unittest.TestCase):
    def test_start_chat_normal(self):
        response = client.post(
            '/api/chat/start',
            json={'message': '', 'current_node_id': 'main_menu', 'mode': 'flow'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('session_id', data)

    def test_start_chat_exception_handling(self):
        with patch('routes.chatbot.process_start', side_effect=Exception('Start error')):
            response = client.post(
                '/api/chat/start',
                json={'message': '', 'current_node_id': 'main_menu', 'mode': 'flow'}
            )
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Layanan chatbot sedang mengalami kendala saat memulai sesi. Silakan coba lagi.')

    def test_chat_exception_handling(self):
        with patch('routes.chatbot.process_chat', side_effect=Exception('Unexpected crash')):
            response = client.post(
                '/api/chat',
                json={'message': 'Halo', 'current_node_id': 'main_menu', 'mode': 'chat'}
            )
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Layanan chatbot sedang mengalami kendala saat memproses pesan Anda. Silakan coba lagi.')

if __name__ == '__main__':
    unittest.main()
