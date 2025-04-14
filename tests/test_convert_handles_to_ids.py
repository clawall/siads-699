import unittest
from unittest.mock import patch, mock_open, MagicMock
from bs4 import BeautifulSoup
import convert_handles_to_ids as converter

class TestConvertHandlesToIds(unittest.TestCase):

    @patch('convert_handles_to_ids.requests.get')
    def test_scrape_page_found(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="grid">
            <a class="box figure-card" href="/figures?id=12345">
                <span href="/user/handle1">handle1</span>
            </a>
        </div>
        '''
        mock_get.return_value = mock_response

        handle_id, next_url = converter.scrape_page(converter.BASE_URL, 'handle1')
        self.assertEqual(handle_id, '12345')
        self.assertIsNone(next_url)

    @patch('convert_handles_to_ids.requests.get')
    def test_scrape_page_not_found(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<div class="grid"></div>'
        mock_get.return_value = mock_response

        handle_id, next_url = converter.scrape_page(converter.BASE_URL, 'handle1')
        self.assertIsNone(handle_id)
        self.assertIsNone(next_url)

    @patch('convert_handles_to_ids.requests.get')
    def test_scrape_page_with_pagination(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="grid"></div>
        <a class="pagination-next" href="/figures?page=2">Next</a>
        '''
        mock_get.return_value = mock_response

        handle_id, _ = converter.scrape_page(converter.BASE_URL, 'handle1')
        self.assertIsNone(handle_id)

    @patch('builtins.open', new_callable=mock_open, read_data='handle1\nhandle2\n')
    @patch('convert_handles_to_ids.requests.get')
    def test_scrape_polititweet(self, mock_get, mock_file):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="grid">
            <a class="box figure-card" href="/figures?id=12345">
                <span href="/user/handle1">handle1</span>
            </a>
        </div>
        '''
        mock_get.return_value = mock_response

        result = converter.scrape_polititweet('handles.csv')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['handle'], 'handle1')
        self.assertEqual(result[0]['id'], '12345')

    @patch('convert_handles_to_ids.requests.get')
    def test_extract_twitter_id_found(self, mock_get):
        # Mock the BeautifulSoup object
        html_content = '''
        <div class="grid">
            <a class="box figure-card" href="/figures?id=12345">
                <span href="/user/handle1">handle1</span>
            </a>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        twitter_id = converter.extract_twitter_id('handle1', soup)
        self.assertEqual(twitter_id, '12345')

    def test_extract_twitter_id_not_found(self):
        # Mock the BeautifulSoup object
        html_content = '<div class="grid"></div>'
        soup = BeautifulSoup(html_content, 'html.parser')
        twitter_id = converter.extract_twitter_id('handle1', soup)
        self.assertIsNone(twitter_id)

if __name__ == '__main__':
    unittest.main()