import unittest
from unittest.mock import patch,MagicMock
from datetime import datetime,timezone
import feedback_discord as f
class DeliveryTests(unittest.TestCase):
 def test_missing_webhook_does_not_call(self):
  with patch.dict(f.os.environ,{'DISCORD_FEEDBACK_WEBHOOK':''}),patch.object(f.requests,'post') as post:
   f.deliver_feedback();post.assert_not_called()
 def test_success_disables_mentions_and_marks_sent(self):
  with patch.dict(f.os.environ,{'DISCORD_FEEDBACK_WEBHOOK':'https://discord.com/api/webhooks/test/test'}),patch.object(f,'connection') as db,patch.object(f.requests,'post',return_value=MagicMock(status_code=200)) as post:
   db.return_value.__enter__.return_value.execute.return_value.fetchone.return_value={'id':'test','rating':5,'comment':'@everyone test','language':'vi','created_at':datetime.now(timezone.utc)}
   f.deliver_feedback()
   self.assertEqual(post.call_args.kwargs['json']['allowed_mentions'],{'parse':[]})
   self.assertIn('discord_sent_at=now()',db.return_value.__enter__.return_value.execute.call_args.args[0])
 def test_failure_keeps_delivery_pending(self):
  with patch.dict(f.os.environ,{'DISCORD_FEEDBACK_WEBHOOK':'https://discord.com/api/webhooks/test/test'}),patch.object(f,'connection') as db,patch.object(f.requests,'post',side_effect=f.requests.Timeout):
   db.return_value.__enter__.return_value.execute.return_value.fetchone.return_value={'id':'test','rating':5,'comment':'test','language':'en','created_at':datetime.now(timezone.utc)}
   f.deliver_feedback()
   self.assertNotIn('discord_sent_at=now()',db.return_value.__enter__.return_value.execute.call_args.args[0])
