import unittest
from unittest.mock import patch,MagicMock
import ai_provider
import news_provider_guard

class OllamaTests(unittest.TestCase):
    def test_local_never_sends_zai_key(self):
        with patch.dict(ai_provider.os.environ,{'AI_PROVIDER':'ollama','OLLAMA_MODEL':'qwen2.5:3b','OLLAMA_BASE_URL':'http://127.0.0.1:11434'}),patch.object(ai_provider.requests,'post') as post:
            ai_provider.completion({'messages':[]},key='secret',stream=True)
            self.assertEqual(post.call_args.args[0],'http://127.0.0.1:11434/v1/chat/completions')
            self.assertNotIn('Authorization',post.call_args.kwargs['headers'])
            self.assertEqual(post.call_args.kwargs['json']['model'],'qwen2.5:3b')
    def test_old_cloud_pause_does_not_block_local(self):
        with patch.dict(ai_provider.os.environ,{'AI_PROVIDER':'ollama'}),patch.object(news_provider_guard,'connection') as conn:
            self.assertIsNone(news_provider_guard.provider_state());conn.assert_not_called()
    def test_local_requires_structured_output(self):
        with patch.dict(ai_provider.os.environ,{'AI_PROVIDER':'ollama'}):
            self.assertEqual(ai_provider.json_format('summary')['type'],'json_schema')
