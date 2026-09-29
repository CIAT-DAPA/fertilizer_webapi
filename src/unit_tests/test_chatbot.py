import json
import unittest
from unittest import mock

from agroadvisory_api import app
from api_modules import chatbot as chatbot_module
from unit_tests.mongo_test_setup import use_mongomock, teardown_mongomock


def _upstream(status_code, payload):
    response = mock.Mock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def _assistant_payload(reply):
    return {'choices': [{'message': {'content': json.dumps(reply)}}]}


class TestChatbot(unittest.TestCase):

    def setUp(self):
        use_mongomock()
        self.app = app.test_client()
        chatbot_module.reset_rate_limiter()

    def tearDown(self):
        teardown_mongomock()

    def test_returns_503_when_key_not_configured(self):
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': ''}):
            response = self.app.post('/chatbot/message', json={'message': 'hello'})
        self.assertEqual(503, response.status_code)
        self.assertEqual('llm_not_configured', response.get_json()['error']['code'])

    def test_rejects_missing_message(self):
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch.object(chatbot_module.requests, 'post') as post:
            response = self.app.post('/chatbot/message', json={})
        self.assertEqual(400, response.status_code)
        post.assert_not_called()

    def test_rejects_non_json_body(self):
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch.object(chatbot_module.requests, 'post') as post:
            response = self.app.post('/chatbot/message', data='message=hello',
                                     headers={'Content-Type': 'text/plain'})
        self.assertEqual(400, response.status_code)
        post.assert_not_called()

    def test_proxies_to_openai_with_server_side_prompt_and_key(self):
        reply = {
            'response': 'Great, wheat on 2 ha. Please allow GPS so I can use your location.',
            'extracted_data': {'crop': 'wheat', 'coordinates': None, 'farm_size_ha': 2},
            'missing_data': ['coordinates'],
            'next_action': 'collect_data',
        }
        with mock.patch.dict(chatbot_module.config,
                             {'OPENAI_API_KEY': 'test-key', 'OPENAI_CHAT_MODEL': 'gpt-4o-mini'}), \
                mock.patch.object(chatbot_module.requests, 'post',
                                  return_value=_upstream(200, _assistant_payload(reply))) as post:
            response = self.app.post('/chatbot/message', json={
                'message': 'I grow wheat on 2 ha',
                'conversation_context': 'Bot: Hello!\nUser: hi',
                'crops': ['Wheat', 'Maize', 'Teff', 'Barley'],
                'collected_data': {'crop': None, 'coordinates': None, 'farmSizeHa': None},
                'session_complete': False,
            })

        self.assertEqual(200, response.status_code)
        body = response.get_json()
        self.assertEqual(reply['response'], body['response'])
        self.assertEqual('collect_data', body['next_action'])
        self.assertEqual(['coordinates'], body['missing_data'])
        self.assertEqual('wheat', body['extracted_data']['crop'])

        # The key only ever travels to OpenAI, never back to the client.
        kwargs = post.call_args.kwargs
        self.assertEqual('Bearer test-key', kwargs['headers']['Authorization'])
        self.assertNotIn('test-key', response.get_data(as_text=True))

        # Prompt/model are pinned on the server and include the app state.
        sent = kwargs['json']
        self.assertEqual('gpt-4o-mini', sent['model'])
        self.assertEqual({'type': 'json_object'}, sent['response_format'])
        self.assertEqual('system', sent['messages'][0]['role'])
        self.assertIn('Available crops: Wheat, Maize, Teff, Barley', sent['messages'][0]['content'])
        self.assertIn('Session status: COLLECTING_OR_NEW', sent['messages'][0]['content'])
        self.assertEqual('Bot: Hello!\nUser: hi\n\nUser: I grow wheat on 2 ha',
                         sent['messages'][1]['content'])

    def test_tolerates_non_json_assistant_content(self):
        payload = {'choices': [{'message': {'content': 'Sorry, plain text answer.'}}]}
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch.object(chatbot_module.requests, 'post', return_value=_upstream(200, payload)):
            response = self.app.post('/chatbot/message', json={'message': 'hello'})
        self.assertEqual(200, response.status_code)
        body = response.get_json()
        self.assertEqual('Sorry, plain text answer.', body['response'])
        self.assertEqual('collect_data', body['next_action'])
        self.assertEqual({}, body['extracted_data'])

    def test_passes_through_upstream_rate_limit_as_429(self):
        payload = {'error': {'message': 'Rate limit reached for gpt-4o-mini', 'type': 'requests'}}
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch.object(chatbot_module.requests, 'post', return_value=_upstream(429, payload)):
            response = self.app.post('/chatbot/message', json={'message': 'hello'})
        self.assertEqual(429, response.status_code)
        self.assertEqual('upstream_rate_limited', response.get_json()['error']['code'])

    def test_maps_other_upstream_errors_to_502_without_leaking_key(self):
        payload = {'error': {'message': 'Incorrect API key provided', 'code': 'invalid_api_key'}}
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'sk-secret-value'}), \
                mock.patch.object(chatbot_module.requests, 'post', return_value=_upstream(401, payload)):
            response = self.app.post('/chatbot/message', json={'message': 'hello'})
        self.assertEqual(502, response.status_code)
        self.assertEqual('upstream_error', response.get_json()['error']['code'])
        self.assertNotIn('sk-secret-value', response.get_data(as_text=True))

    def test_maps_timeout_to_504(self):
        with mock.patch.dict(chatbot_module.config, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch.object(chatbot_module.requests, 'post',
                                  side_effect=chatbot_module.requests.Timeout()):
            response = self.app.post('/chatbot/message', json={'message': 'hello'})
        self.assertEqual(504, response.status_code)

    def test_rate_limits_per_client(self):
        reply = {'response': 'ok', 'extracted_data': {}, 'missing_data': [], 'next_action': 'collect_data'}
        with mock.patch.dict(chatbot_module.config,
                             {'OPENAI_API_KEY': 'test-key', 'CHATBOT_RATE_LIMIT_PER_MINUTE': 2}), \
                mock.patch.object(chatbot_module.requests, 'post',
                                  return_value=_upstream(200, _assistant_payload(reply))) as post:
            codes = [self.app.post('/chatbot/message', json={'message': 'hi'}).status_code
                     for _ in range(3)]
            # A different client (via X-Forwarded-For, as behind nginx) is not affected.
            other = self.app.post('/chatbot/message', json={'message': 'hi'},
                                  headers={'X-Forwarded-For': '203.0.113.9'})
        self.assertEqual([200, 200, 429], codes)
        self.assertEqual(200, other.status_code)
        self.assertEqual(3, post.call_count)


if __name__ == "__main__":
    unittest.main()
