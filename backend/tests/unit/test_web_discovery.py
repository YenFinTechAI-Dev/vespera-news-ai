import unittest
from web_discovery import parse_results, Search
from pydantic import ValidationError
class DiscoveryTests(unittest.TestCase):
    def item(self,url,date='Mon, 01 Jan 2024 10:00:00 GMT'):
        return f'<item><link>{url}</link><title>Machine learning</title><pubDate>{date}</pubDate><source>Example</source><description>Preview only</description></item>'
    def test_deduplication_and_unsafe_links(self):
        valid=self.item('https://news.google.com/rss/articles/example')
        unsafe=self.item('https://news.google.com.evil.test/item')
        future=self.item('https://news.google.com/rss/articles/future','Fri, 01 Jan 2100 00:00:00 GMT')
        data=parse_results(('<rss><channel>'+valid+valid+unsafe+future+'</channel></rss>').encode())
        self.assertEqual(len(data),1);self.assertEqual(data[0]['publisher'],'Example')
    def test_entities_rejected(self):
        with self.assertRaises(ValueError):parse_results(b'<!DOCTYPE rss [<!ENTITY x "x">]><rss/>')
    def test_query_size_is_bounded(self):
        self.assertEqual(len(Search(query='x'*500).query),500)
        with self.assertRaises(ValidationError):Search(query='x'*501)
if __name__=='__main__':unittest.main()
