import pandas as pd
import argparse
import re
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'https://polititweet.org/tweets'

def extract_tweet_data(soup):
    # 1. Find main tweets grid
    tweets_grid = soup.find('div', {'class': 'grid'})
    
    if not tweets_grid:
        print('Could not find the tweets grid on page.')
        return
    
    # 2. Extract tweets from the anchor tags, which are the tweet cards.
    tweet_cards = tweets_grid.find_all('a', {'class': 'box tweet-card'})
    if not tweet_cards:
        print(f'Could not find the tweet cards on the grid.')
        return
    
    all_tweets = []
    
    for element in tweet_cards:
        tweet_data = {}

        # 1. Metadata are in <span> tags.
        date = element.find('span', string=re.compile(r'^Posted'))
        tweet_data['tweeted_at'] = date.get_text(strip=True) if date else None

        # Second is user handle
        user_handle = element.find('span', href=True)
        tweet_data['user_handle'] = user_handle.get_text(strip=True) if user_handle else None

        # Third is a retweet flag
        retweet = element.find('span', string='Retweet')
        tweet_data['is_retweet'] = True if retweet else False

        # 2. Tweet text are in <p> tags.
        p_tags = element.find_all('p')

        # 3. Extract the text from each <p>. First <p> is the username, second is the tweet content.
        if len(p_tags) == 2:
            tweet_data['username'] = p_tags[0].find('strong').get_text(strip=True)

            if p_tags[1].span:
                p_tags[1].span.decompose()
            tweet_data['text'] = p_tags[1].get_text(strip=True)

        all_tweets.append(tweet_data)

    return all_tweets

def scrape_page(url):
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        print(f'Failed to retrieve {url}: status {response.status_code}')
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    page_tweets = extract_tweet_data(soup)

    next_link = soup.find('a', {'class': 'pagination-next'}, string='Next')

    return page_tweets, next_link.get('href') if next_link else None

def scrape_polititweet(account_id, max_pages=None):
    pages = 0
    all_tweets = []
    next_url = f'?account={account_id}'

    while next_url:
        print(f'Scraping page {next_url}...')
        page_tweets, next_url = scrape_page(f'{BASE_URL}{next_url}')

        all_tweets.extend(page_tweets)
        
        # Delay to be kind to the server
        time.sleep(.5)

        pages += 1
        if max_pages and pages >= max_pages:
            break
    
    print(f'Scraped {len(all_tweets)} tweets total.')
    return all_tweets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawls over PolitTweet.org to query tweets from a person.')
    parser.add_argument('account_id', type=str, help='Twitter\'s account ID to scrape.')
    parser.add_argument('outputname', type=str, help='The name of the file to output.')
    parser.add_argument('--max_pages', type=int, help='The total amount of pages to scrape, if not all.', default=None)
    args = parser.parse_args()

    tweets = scrape_polititweet(args.account_id, max_pages=args.max_pages)

    df = pd.DataFrame(tweets)
    df.to_csv(args.outputname, index=False)
