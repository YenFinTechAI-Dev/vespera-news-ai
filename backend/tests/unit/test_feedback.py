import unittest
from uuid import uuid4
from unittest.mock import patch,MagicMock
from pydantic import ValidationError
from fastapi import HTTPException
from news_feedback import Feedback,submit,report

class FeedbackTests(unittest.TestCase):
    def test_bounds(self):
        for rating in (0,6,True,'5'):
            with self.assertRaises(ValidationError):Feedback(id=uuid4(),rating=rating)
        with self.assertRaises(ValidationError):Feedback(id=uuid4(),rating=5,comment='a'*2001)
    def test_submission_idempotency(self):
        body=Feedback(id=uuid4(),rating=4,comment=' useful ')
        with patch('news_feedback.gateway'),patch('news_feedback.throttle'),patch('news_feedback.connection') as db:
            self.assertEqual(submit(body,'gateway','client'),{'status':'received'})
            sql,args=db.return_value.__enter__.return_value.execute.call_args.args
            self.assertIn('ON CONFLICT(id) DO NOTHING',sql)
            self.assertEqual(args[0],body.id)
            self.assertEqual(args[2],'useful')
    def test_report_requires_gateway(self):
        with patch('news_feedback.gateway',side_effect=HTTPException(401,'unauthorized')),patch('news_feedback.connection') as db:
            with self.assertRaises(HTTPException):report(None)
            db.assert_not_called()

if __name__=='__main__':unittest.main()
