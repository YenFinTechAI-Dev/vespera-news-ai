import unittest
from language_check import check_answer_language
class LanguageTests(unittest.TestCase):
    def test_reject_english_in_vietnamese_mode(self):
        with self.assertRaises(ValueError):check_answer_language({'paragraphs':[{'text':'Machine learning is a field of artificial intelligence that enables computers to learn from data and improve their performance.'}]},'vi')
    def test_vietnamese(self):
        check_answer_language({'paragraphs':[{'text':'Học máy là một lĩnh vực của trí tuệ nhân tạo, giúp máy tính học từ dữ liệu và cải thiện khả năng thực hiện các nhiệm vụ.'}],'limitations':'Nguồn chỉ cung cấp trích đoạn, chưa đủ để đưa ra kết luận về hiệu quả thực tế.'},'vi')
    def test_english(self):
        check_answer_language({'paragraphs':[{'text':'Machine learning is a field of artificial intelligence that enables computers to learn from data and improve their performance.'}]},'en')
