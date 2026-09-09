import unittest
from main import app


class NewsEntrypointTests(unittest.TestCase):
    def test_news_routes_without_market_or_chat(self):
        paths = set(app.openapi()['paths'])
        self.assertIn('/news', paths)
        self.assertIn('/research/synthesize', paths)
        self.assertIn('/news/feedback', paths)
        self.assertFalse(any(path.startswith(('/stocks', '/market', '/chat', '/predict')) for path in paths))


if __name__ == '__main__':
    unittest.main()
