import unittest
from unittest.mock import patch, mock_open
import json
import os
import ai_prompt
from ai_prompt import CONFIG_PATH

class TestConfigHandling(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

    def test_config_creation(self):
        """Test default config creation when missing"""
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        
        config = ai_prompt.load_config()
        self.assertEqual(config, ai_prompt.DEFAULT_CONFIG)
        self.assertTrue(os.path.exists(CONFIG_PATH))

    @patch('ai_prompt.setup_keys_interactive')
    @patch('builtins.input', side_effect=['model_x', 'model_y', 'model_z', 'openai'])
    def test_setup_config(self, mock_input, mock_keys):
        """Test interactive configuration setup"""
        mock_keys.return_value = {
            'openai': 'test_key',
            'openrouter': 'test_key2',
            'anthropic': 'test_key3'
        }
        
        ai_prompt.setup_config()
        
        with open(ai_prompt.CONFIG_PATH) as f:
            config = json.load(f)
            
        self.assertEqual(config['openai']['default_model'], 'model_x')
        self.assertEqual(config['openrouter']['default_model'], 'model_y')

class TestAPIQueries(unittest.TestCase):
    @patch('requests.post')
    def test_successful_openai_query(self, mock_post):
        """Test successful OpenAI API response"""
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {'choices': [{'message': {'content': 'test response'}}]}
        mock_post.return_value = mock_response
        
        result = ai_prompt.query_openai('test prompt', 'gpt-3.5-turbo', 'sk-test')
        self.assertEqual(result, 'test response')

    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        mock_post.side_effect = Exception('API error')
        result = ai_prompt.query_openai('test prompt', 'gpt-3.5-turbo', 'sk-test')
        self.assertIsNone(result)

class TestModelListing(unittest.TestCase):
    @patch('requests.get')
    def test_openrouter_model_list(self, mock_get):
        """Test OpenRouter model listing"""
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {'data': [{'id': 'google/gemini-pro', 'name': 'Gemini Pro'}]}
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            ai_prompt.list_models('openrouter', 'sk-test')
            mock_print.assert_any_call('  - google/gemini-pro (Gemini Pro)')
    @patch('requests.get')
    def test_openai_model_list(self, mock_get):
        """Test OpenAI model listing"""
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {'data': [{'id': 'gpt-4'}, {'id': 'gpt-3.5'}]}
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            ai_prompt.list_models('openai', 'sk-test')
            mock_print.assert_any_call('  - gpt-3.5')
            mock_print.assert_any_call('  - gpt-4')

    def test_anthropic_model_list(self):
        """Test Anthropic model listing"""
        with patch('builtins.print') as mock_print:
            ai_prompt.list_models('anthropic', 'sk-test')
            mock_print.assert_any_call('  - claude-3-opus-20240229')

class TestErrorScenarios(unittest.TestCase):
    def test_missing_api_key(self):
        """Test handling of missing API key"""
        with patch('ai_prompt.load_keys') as mock_load, \
             patch('sys.exit') as mock_exit:
            mock_load.return_value = {'openrouter': ''}
            ai_prompt.main(['-p', 'openrouter'])
            mock_exit.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()