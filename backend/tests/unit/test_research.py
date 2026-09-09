import unittest
from unittest.mock import patch,MagicMock
from uuid import uuid4
from fastapi import HTTPException
import research_api as api

class ResearchTests(unittest.TestCase):
    def test_rejects_invented_and_missing_citations(self):
        for refs in [[],[3],['1'],[True]]:
            with self.assertRaises(ValueError):api.validate_answer({'paragraphs':[{'text':'Claim','sources':refs}]},{1,2})
    def test_valid_references_are_preserved(self):
        answer=api.validate_answer({'paragraphs':[{'text':'Evidence-based statement','sources':[1,2]}],'limitations':'Excerpts only'},{1,2})
        self.assertEqual(answer['paragraphs'][0]['sources'],[1,2])
    def test_title_only_never_calls_provider(self):
        with patch.object(api,'sources_for',return_value=[{'coverage':'title_only'}]),patch.object(api.requests,'post') as post:
            result=api.run(api.Question(query='Education',language='en',source_ids=[uuid4()]),{'id':uuid4()})
        self.assertEqual(result['status'],'insufficient_sources');post.assert_not_called()
    def test_provider_pause_does_not_consume_quota(self):
        sources=[{'number':1,'coverage':'excerpt'},{'number':2,'coverage':'excerpt'}]
        with patch.object(api,'sources_for',return_value=sources),patch.object(api,'connection') as conn,patch.object(api,'provider_state',return_value={'blocked':True,'retry_at':None}),patch.object(api.requests,'post') as post:
            conn.return_value.__enter__.return_value.execute.return_value.fetchone.return_value=None
            result=api.run(api.Question(query='Education',language='en',source_ids=[uuid4()]),{'id':uuid4()})
            self.assertEqual(conn.call_count,1)
        self.assertEqual(result['status'],'provider_paused');post.assert_not_called()
    def test_requires_session(self):
        with patch.object(api,'gateway'),patch.object(api,'identity',side_effect=HTTPException(401)),patch.object(api,'run') as run:
            with self.assertRaises(HTTPException):api.synthesize(api.Question(query='Education',source_ids=[uuid4()]))
            run.assert_not_called()
    def test_success_with_mock_provider_is_stored(self):
        sources=[{'number':1,'coverage':'excerpt'},{'number':2,'coverage':'excerpt'}]
        response=MagicMock(status_code=200)
        response.json.return_value={'choices':[{'finish_reason':'stop','message':{'content':'{"paragraphs":[{"text":"Supported synthesis","sources":[1,2]}],"limitations":"Excerpts only"}'}}]}
        with patch.object(api,'sources_for',return_value=sources),patch.object(api,'connection') as connection,patch.object(api,'provider_state',return_value=None),patch.object(api,'record_success'),patch.dict(api.os.environ,{'AI_PROVIDER':'huggingface','HF_TOKEN':'test-only'}),patch.object(api.requests,'post',return_value=response):
            conn=connection.return_value.__enter__.return_value
            conn.execute.return_value.fetchone.side_effect=[None,{'user_id':'id'},{'requests':1},{'attempts':1}]
            result=api.run(api.Question(query='Education',language='en',source_ids=[uuid4()]),{'id':uuid4()})
            self.assertEqual(result['status'],'ready')
            self.assertIn("status='ready'",conn.execute.call_args.args[0])

if __name__=='__main__':unittest.main()

class GuestResearchTests(unittest.TestCase):
    def test_guest_key_required(self):
        with self.assertRaises(HTTPException):api.guest_identity(None,None)
    def test_guest_identity_stable(self):
        with patch.object(api,'connection'):
            a=api.guest_identity('a'*64,'b'*64)
            b=api.guest_identity('a'*64,'c'*64)
        self.assertEqual(a['id'],b['id'])
        self.assertTrue(a['guest'])
    def test_cached_guest_answer_does_not_spend(self):
        with patch.object(api,'sources_for',return_value=[{'coverage':'excerpt'},{'coverage':'excerpt'}]),patch.object(api,'connection') as db,patch.object(api.ai_provider,'completion') as completion:
            db.return_value.__enter__.return_value.execute.return_value.fetchone.return_value={'answer':{'paragraphs':[]}}
            result=api.run(api.Question(query='topic',source_ids=[uuid4()]),{'id':uuid4(),'guest':True})
            self.assertEqual(result['status'],'ready')
            self.assertEqual(db.call_count,1)
            completion.assert_not_called()
    def test_guest_daily_limit_before_provider(self):
        with patch.object(api,'sources_for',return_value=[{'coverage':'excerpt'},{'coverage':'excerpt'}]),patch.object(api,'connection') as db,patch.object(api,'provider_state',return_value=None),patch.object(api.ai_provider,'available',return_value=True),patch.object(api.ai_provider,'completion') as completion:
            conn=db.return_value.__enter__.return_value
            conn.execute.return_value.fetchone.side_effect=[None,{'user_id':'id'},None]
            with self.assertRaises(HTTPException) as error:api.run(api.Question(query='topic',source_ids=[uuid4()]),{'id':uuid4(),'guest':True,'client':'a'*64})
            self.assertEqual(error.exception.status_code,429)
            self.assertEqual(conn.execute.call_args.args[1][1],5)
            completion.assert_not_called()

