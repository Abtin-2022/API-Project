import unittest

from file1 import article_access, content_extractor, insert_to_db, link_extractor

class TestArticleFunctions(unittest.TestCase):

    def test_article_access(self):
        # Mock response
        class MockResponse:
            def json(self):
                return {'articles': [{'url': 'http://example.com/article1'}]}

        self.assertEqual(article_access(MockResponse()), [{'url': 'http://example.com/article1'}])

    def test_link_extractor(self):
        articles = [{'url': 'http://example.com/article1'}]
        self.assertEqual(link_extractor(articles), 'http://example.com/article1')

    def test_content_extractor(self):
        content = [{'content': 'This is a test article.'}]
        self.assertEqual(content_extractor(content), 'This is a test article.')

    def test_insert_to_db(self):
        engine = db.create_engine('sqlite:///out.db')

        insert_to_db("general", "This is a test article.", engine)

        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM articles WHERE category='general'").fetchall()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['content'], "This is a test article.")

if __name__ == '__main__':
    unittest.main()
