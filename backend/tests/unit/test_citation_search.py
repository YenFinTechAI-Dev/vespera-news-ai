import unittest
from discovery_sources import search_text

class CitationSearchTests(unittest.TestCase):
    def test_extracts_vietnamese_work_title(self):
        query='Nguyễn Thị Nhàn. (2025). Phát triển tài chính xanh dựa trên ứng dụng công nghệ tài chính và các hàm ý chính sách cho Việt Nam. Tạp chí Quản lý nhà nước, đăng ngày 11/03/2025.'
        self.assertEqual(search_text(query),'Phát triển tài chính xanh dựa trên ứng dụng công nghệ tài chính và các hàm ý chính sách cho Việt Nam')
    def test_regular_query_is_unchanged(self):
        self.assertEqual(search_text('machine learning education'),'machine learning education')
