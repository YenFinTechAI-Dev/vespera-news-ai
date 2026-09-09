import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import social_auth as auth

class SocialAuthTests(unittest.TestCase):
    def test_google_requires_nonce_and_verified_email(self):
        for claims in [{'sub':'1','email':'a@example.com','nonce':'wrong','email_verified':True}, {'sub':'1','email':'a@example.com','nonce':'expected','email_verified':False}]:
            with patch.object(auth.id_token, 'verify_oauth2_token', return_value=claims):
                with self.assertRaises(ValueError):
                    auth.google_profile('token','expected')

    def test_google_verified_audience(self):
        with patch.object(auth, 'config', return_value=('expected-client','')), patch.object(auth.id_token, 'verify_oauth2_token', return_value={'sub':'1','email':'a@example.com','nonce':'nonce','email_verified':True}) as verify:
            self.assertEqual(auth.google_profile('token','nonce')[:2], ('1','a@example.com'))
            self.assertEqual(verify.call_args.args[2], 'expected-client')

    def test_invalid_signature_does_not_create_session(self):
        with patch.object(auth,'gateway'), patch.object(auth,'enabled',return_value=True), patch.object(auth,'throttle'), patch.object(auth,'consume',return_value={'nonce':'nonce'}), patch.object(auth.id_token,'verify_oauth2_token',side_effect=ValueError()), patch.object(auth,'social_session') as session:
            with self.assertRaises(HTTPException) as error:
                auth.complete('google',auth.Completion(state='x'*32,credential='bad'))
            self.assertEqual(error.exception.status_code,401)
            session.assert_not_called()

    def test_state_cannot_be_replayed(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.return_value=None
        with patch.object(auth,'connection') as connection:
            connection.return_value.__enter__.return_value=conn
            with self.assertRaises(HTTPException): auth.consume('google','used')
            self.assertIn('DELETE FROM app_oauth_attempts',conn.execute.call_args.args[0])

    def test_existing_email_is_not_automatically_linked(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.side_effect=[None,{'id':'existing'}]
        with patch.object(auth,'connection') as connection, patch.object(auth,'session_for') as session:
            connection.return_value.__enter__.return_value=conn
            with self.assertRaises(HTTPException) as error: auth.social_session('google','subject','a@example.com','Name')
            self.assertEqual(error.exception.status_code,409)
            session.assert_not_called()

if __name__=='__main__': unittest.main()
