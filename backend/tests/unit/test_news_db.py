import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import database
import news_api
from fastapi import HTTPException


class NewsTests(unittest.TestCase):
    def test_missing_configuration_is_safe(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            with self.assertRaises(database.DatabaseUnavailable):
                with database.connection():
                    pass
            with self.assertRaises(HTTPException) as result:
                news_api.health()
            self.assertEqual(result.exception.status_code, 503)

    def test_driver_error_does_not_expose_credentials(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@example/test"}), patch(
            "database.psycopg.connect", side_effect=database.psycopg.OperationalError("SECRET_PASSWORD")
        ):
            with self.assertRaises(database.DatabaseUnavailable) as result:
                with database.connection():
                    pass
            self.assertNotIn("SECRET_PASSWORD", str(result.exception))

    def test_news_filters_are_parameterized_and_drafts_hidden(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = {"count": 0}
        conn.execute.return_value.fetchall.return_value = []
        with patch("news_api.connection") as context:
            context.return_value.__enter__.return_value = conn
            result = news_api.list_news(news_api.Category.technology, news_api.Language.vi, 20, 0)
        self.assertEqual(result["items"], [])
        sql, params = conn.execute.call_args.args
        self.assertIn("a.status = 'published'", sql)
        self.assertIn("a.published_at <= CURRENT_TIMESTAMP", sql)
        self.assertEqual(params, ["vi", "technology", 20, 0])

    def test_missing_article_returns_404(self):
        from uuid import uuid4
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        with patch("news_api.connection") as context:
            context.return_value.__enter__.return_value = conn
            with self.assertRaises(HTTPException) as result:
                news_api.get_news(uuid4(), news_api.Language.en)
            self.assertEqual(result.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
