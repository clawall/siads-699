import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import time
import csv

SLEEP_TIMEOUT_SECONDS = .1
BASE_URL = 'https://polititweet.org'

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
        
        tweet = requests.get(f'{BASE_URL}{element.get("href")}&raw=True', timeout=10)
        if tweet.status_code != 200:
            print(f'Failed to retrieve tweet: status {tweet.status_code}')
            continue
        tweet_data = tweet.json()

        # # 1. Metadata are in <span> tags.
        # date = element.find('span', string=re.compile(r'^Posted'))
        # tweet_data['tweeted_at'] = date.get_text(strip=True) if date else None

        # # Second is user handle
        # user_handle = element.find('span', href=True)
        # tweet_data['user_handle'] = user_handle.get_text(strip=True) if user_handle else None

        # # Third is a retweet flag
        # retweet = element.find('span', string='Retweet')
        # tweet_data['is_retweet'] = True if retweet else False

        # # 2. Tweet text are in <p> tags.
        # p_tags = element.find_all('p')

        # # 3. Extract the text from each <p>. First <p> is the username, second is the tweet content.
        # if len(p_tags) == 2:
        #     tweet_data['username'] = p_tags[0].find('strong').get_text(strip=True)

        #     if p_tags[1].span:
        #         p_tags[1].span.decompose()
        #     tweet_data['text'] = p_tags[1].get_text(strip=True)

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
        try:
            page_tweets, next_url = scrape_page(f'{BASE_URL}/tweets{next_url}')

            all_tweets.extend(page_tweets)
        except Exception as e:
            print(f'Error scraping page: {e}')
            break
        
        # Delay to be kind to the server
        time.sleep(SLEEP_TIMEOUT_SECONDS)

        pages += 1
        if max_pages and pages >= max_pages:
            break
    
    print(f'Scraped {len(all_tweets)} tweets total.')
    return all_tweets

def scrape_all_tweets(account_id_file, output_folder, max_pages=None):
    with open(account_id_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader) # Skip header

        for account_ids in reader:
            account_id = account_ids[0]
            tweets = scrape_polititweet(account_id, max_pages=max_pages)
            df = pd.DataFrame(tweets)
            df.to_csv(f'{output_folder}/{account_id}.csv', index=False)

            # Delay to be kind to the server
            time.sleep(SLEEP_TIMEOUT_SECONDS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawls over PolitTweet.org to query tweets from a person.')
    parser.add_argument('account_id_file', type=str, help='File containg Twitter\'s account ID to scrape.')
    parser.add_argument('output_folder', type=str, help='The name of the folder to output CSV files.')
    parser.add_argument('--max_pages', type=int, help='The total amount of pages to scrape, if not all.', default=None)
    args = parser.parse_args()

    scrape_all_tweets(args.account_id_file, args.output_folder, max_pages=args.max_pages)
