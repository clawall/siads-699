import unittest
from unittest.mock import patch, mock_open, MagicMock
from bs4 import BeautifulSoup

from read_tweets import (
    extract_tweet_data,
    scrape_page,
    scrape_polititweet,
    scrape_all_tweets,
    BASE_URL
)


class TestReadTweets(unittest.TestCase):

    @patch('read_tweets.requests.get')
    def test_extract_tweet_data(self, mock_get):
        # Mock BeautifulSoup object
        html_content = '''
        <div class="grid">
            <a class="box tweet-card" href="/tweet/12345"></a>
            <a class="box tweet-card" href="/tweet/67890"></a>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')

        # Mock tweet responses
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "12345", "text": "Tweet 1"}),
            MagicMock(status_code=200, json=lambda: {"id": "67890", "text": "Tweet 2"})
        ]

        tweets = extract_tweet_data(soup)
        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweets[0]['id'], "12345")
        self.assertEqual(tweets[1]['id'], "67890")

    @patch('read_tweets.requests.get')
    def test_scrape_page(self, mock_get):
        # Mock page response
        html_content = '''
        <div class="grid">
            <a class="box tweet-card" href="/tweet/12345"></a>
        </div>
        <a class="pagination-next" href="/tweets?page=2">Next</a>
        '''
        mock_get.return_value = MagicMock(status_code=200, text=html_content)

        tweets, next_url = scrape_page(f'{BASE_URL}/tweets?page=1')
        self.assertEqual(len(tweets), 1)
        self.assertEqual(next_url, "/tweets?page=2")

    @patch('read_tweets.scrape_page')
    def test_scrape_polititweet(self, mock_scrape_page):
        # Mock scrape_page behavior
        mock_scrape_page.side_effect = [
            ([{"id": "12345", "text": "Tweet 1"}], "/tweets?page=2"),
            ([{"id": "67890", "text": "Tweet 2"}], None)
        ]

        tweets = scrape_polititweet("test_account", max_pages=2)
        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweets[0]['id'], "12345")
        self.assertEqual(tweets[1]['id'], "67890")

    @patch('read_tweets.scrape_polititweet')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.DataFrame.to_csv')
    def test_scrape_all_tweets(self, mock_to_csv, mock_open_file, mock_scrape_polititweet):
        # Mock CSV file content
        mock_open_file.return_value.__enter__.return_value = iter([
            "account_id\n",
            "test_account_1\n",
            "test_account_2\n"
        ])

        # Mock scrape_polititweet behavior
        mock_scrape_polititweet.side_effect = [
            [{"id": "12345", "text": "Tweet 1"}],
            [{"id": "67890", "text": "Tweet 2"}]
        ]

        scrape_all_tweets("test_accounts.csv", "output_folder", max_pages=1)

        # Check if DataFrame.to_csv was called twice
        self.assertEqual(mock_to_csv.call_count, 2)
        mock_to_csv.assert_any_call('output_folder/test_account_1.csv', index=False)
        mock_to_csv.assert_any_call('output_folder/test_account_2.csv', index=False)

    @patch('read_tweets.requests.get')
    def test_scrape_page_failure(self, mock_get):
        # Mock failed response
        mock_get.return_value = MagicMock(status_code=404)

        tweets, next_url = scrape_page(f'{BASE_URL}/tweets?page=1')
        self.assertIsNone(tweets)
        self.assertIsNone(next_url)

    @patch('read_tweets.requests.get')
    def test_extract_tweet_data_no_grid(self, mock_get):
        # Mock BeautifulSoup object with no grid
        html_content = '<div class="no-grid"></div>'
        soup = BeautifulSoup(html_content, 'html.parser')

        tweets = extract_tweet_data(soup)
        self.assertIsNone(tweets)

    @patch('read_tweets.requests.get')
    def test_extract_tweet_data_no_tweet_cards(self, mock_get):
        # Mock BeautifulSoup object with no tweet cards
        html_content = '<div class="grid"></div>'
        soup = BeautifulSoup(html_content, 'html.parser')

        tweets = extract_tweet_data(soup)
        self.assertIsNone(tweets)


if __name__ == '__main__':
    unittest.main()