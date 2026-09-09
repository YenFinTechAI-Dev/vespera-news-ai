import unittest
from search_relevance import relevant

class SearchRelevanceTests(unittest.TestCase):
    def test_named_bank_requires_mb_anchor(self):
        self.assertFalse(relevant('số liệu ngân hàng mb bank','Bảo vệ dữ liệu khách hàng trong hoạt động ngân hàng','ngân hàng số và dữ liệu'))
        self.assertTrue(relevant('số liệu ngân hàng mb bank','MB Bank công bố báo cáo tài chính','Số liệu hoạt động của MB Bank'))
    def test_general_topic_keeps_related_result(self):
        self.assertTrue(relevant('machine learning','Machine learning in education','methods and models'))
    def test_long_title_rejects_loose_word_overlap(self):
        query='Phát triển tài chính xanh dựa trên ứng dụng công nghệ tài chính'
        self.assertFalse(relevant(query,'Tác động của ứng dụng công nghệ tài chính đến hiệu quả hoạt động ngân hàng','ngân hàng thương mại Việt Nam'))
        self.assertTrue(relevant(query,'Phát triển tài chính xanh dựa trên ứng dụng công nghệ tài chính','chính sách cho Việt Nam'))

if __name__=='__main__': unittest.main()
