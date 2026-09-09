import unittest
from unittest.mock import patch,MagicMock
import news_worker
import news_provider_guard
class ProviderBackoffTests(unittest.TestCase):
    def test_paused_provider_does_not_spend_budget(self):
        with patch('news_worker.ai_writer._available',return_value=True),patch('news_worker.provider_state',return_value={'blocked':True}),patch('news_worker.connection') as db,patch('news_worker.ai_writer.rewrite') as ai:
            self.assertEqual(news_worker.process_one(),'provider_paused');db.assert_not_called();ai.assert_not_called()
    def test_rate_limit_has_shared_cooldown(self):
        with patch('news_provider_guard.connection') as db:
            news_provider_guard.record_failure(429)
            args=db.return_value.__enter__.return_value.execute.call_args.args
            self.assertEqual(args[1],['rate_limited',429,30])
            self.assertNotIn('news_ai_usage',args[0])
    def test_invalid_key_backs_off_longer(self):
        with patch('news_provider_guard.connection') as db:
            news_provider_guard.record_failure(401)
            self.assertEqual(db.return_value.__enter__.return_value.execute.call_args.args[1],['authorization',401,360])
if __name__=='__main__':unittest.main()
