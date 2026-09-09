import os
import unittest
from unittest.mock import patch
import ai_provider
import news_provider_guard

class HuggingFaceTests(unittest.TestCase):
    def test_routes_token_only_to_huggingface(self):
        with patch.dict(os.environ, {'AI_PROVIDER':'huggingface','HF_TOKEN':'test-hf','HF_MODEL':'test-model'},clear=True), patch.object(ai_provider.requests,'post') as post:
            self.assertTrue(ai_provider.available())
            ai_provider.completion({'messages':[]},key='old-zai-secret')
            self.assertEqual(post.call_args.args[0],'https://router.huggingface.co/v1/chat/completions')
            self.assertEqual(post.call_args.kwargs['headers']['Authorization'],'Bearer test-hf')
            self.assertEqual(post.call_args.kwargs['json']['model'],'test-model')
            self.assertFalse(post.call_args.kwargs['allow_redirects'])

    def test_missing_hf_key_does_not_use_zai(self):
        with patch.dict(os.environ, {'AI_PROVIDER':'huggingface','ZAI_API_KEY':'old-secret'},clear=True), patch.object(ai_provider.requests,'post') as post:
            self.assertFalse(ai_provider.available())
            with self.assertRaises(ValueError):ai_provider.completion({'messages':[]})
            post.assert_not_called()

    def test_old_provider_pause_is_scoped(self):
        with patch.dict(os.environ, {'AI_PROVIDER':'huggingface'}),patch.object(news_provider_guard,'connection') as connection:
            news_provider_guard.provider_state()
            call=connection.return_value.__enter__.return_value.execute.call_args
            self.assertIn('provider_name=%s',call.args[0])
            self.assertEqual(call.args[1],['huggingface'])
