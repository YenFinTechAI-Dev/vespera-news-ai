import unittest
from unittest.mock import patch
from discovery_sources import aggregate, safe_url, research

class DiscoveryTests(unittest.TestCase):
    def test_unsafe_and_removed_sources(self):
        for value in ['javascript:alert(1)','https://127.0.0.1/a','https://localhost/a','https://x.com/a','https://user:pass@example.com']:
            self.assertFalse(safe_url(value))
        self.assertTrue(safe_url('https://doi.org/10.1/paper'))
    def test_missing_abstract_has_nonempty_preview(self):
        row=dict(url='https://doi.org/10.1/paper',title='Paper',summary='',publisher='Journal',published=None)
        with patch('discovery_sources.research',return_value=[row]):
            items,status=aggregate('Paper','en','research',lambda *_:[])
        self.assertEqual(items[0]['summary'],'Paper')
        self.assertIsNone(items[0]['published'])
    def test_provider_failure_preserves_other_results(self):
        row=dict(url='https://example.com/a',title='Travel',summary='Travel',publisher='Example',published=None)
        with patch('discovery_sources.research',side_effect=ValueError()),patch('discovery_sources.web',return_value=[row]):
            items,status=aggregate('travel','en','all',lambda *_:[])
        self.assertEqual(len(items),1)
        self.assertEqual(status['research'],'unavailable')
