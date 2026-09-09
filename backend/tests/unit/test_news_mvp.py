import unittest
from datetime import datetime,timezone,timedelta
from news_mvp import cluster,provenance,match_interest

class NewsMVPTests(unittest.TestCase):
    def row(self,title,days=0):
        return dict(id=title,title=title,original_title=title,summary='',category='ai',
                    published_at=datetime(2026,9,8,tzinfo=timezone.utc)+timedelta(days=days),source_url='https://openai.com/news/test')
    def test_same_event(self):
        rows=[self.row('Acme launches new GPU compiler for developers'),self.row('Acme launches new GPU compiler for developers today')]
        self.assertEqual(len(cluster(rows)),1)
    def test_different_numbers_or_dates_stay_separate(self):
        self.assertEqual(len(cluster([self.row('Acme launches model version 2 for developers'),self.row('Acme launches model version 3 for developers')])),2)
        self.assertEqual(len(cluster([self.row('Acme launches GPU compiler for developers'),self.row('Acme launches GPU compiler for developers',4)])),2)
    def test_lookalike_domain_not_trusted(self):
        self.assertEqual(provenance('https://openai.com.attacker.org/a')['tier'],'unreviewed')
        self.assertEqual(provenance('https://arxiv.org/abs/123')['tier'],'preprint')
        self.assertEqual(provenance('https://author.medium.com/post')['tier'],'community')
    def test_multiword_interest(self):
        self.assertTrue(match_interest(self.row('Machine learning advances'),{'term':'machine learning'}))
        self.assertFalse(match_interest(self.row('Machine definition'),{'term':'machine learning'}))
        self.assertFalse(match_interest(self.row('Anything'),{'term':'the'}))

if __name__=='__main__':unittest.main()
