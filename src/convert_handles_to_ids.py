import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = 'https://polititweet.org/figures'

def extract_twitter_id(handle, soup):
    # 1. Find main tweets grid
    tweets_grid = soup.find('div', {'class': 'grid'})
    
    if not tweets_grid:
        print('...NOT FOUND!')
        return
    
    # 2. Extract ids from the anchor tags, which are the tweet cards.
    figure_cards = tweets_grid.find_all('a', {'class': 'box figure-card'})
    if not figure_cards:
        print('...NOT FOUND!')
        return
    
    for element in figure_cards:
        user_handle = element.find('span', href=True)['href'].split('/')[-1]
        
        if user_handle == handle:
            figure_url = element['href'].split('=')[-1]
            print(f'...FOUND! {figure_url}')
            return figure_url

    return None

def scrape_page(url, handle):
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        print(f'Failed to retrieve {url}: status {response.status_code}')
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    handle_id = extract_twitter_id(handle, soup)

    if not handle_id:
        return None, soup.find('a:not([disabled])', {'class': 'pagination-next'}, string='Next')

    return handle_id, None

def scrape_polititweet(handle_file, max_pages=None):
    with open(handle_file, 'r') as csv_file:
        reader = csv.reader(csv_file)

        all_ids = []
        for handles in reader:
            handle = handles[0]
            print(f'Scraping page for {handle}...', end='')
            pages = 0
            next_url = f'?search={handle}'

            while next_url:
                try:
                    handle_id, next_url = scrape_page(f'{BASE_URL}{next_url}', handle)

                    if handle_id:
                        all_ids.append({'id': handle_id, 'handle': handle})
                        break
                    
                    # Delay to be kind to the server
                    time.sleep(.1)

                    pages += 1
                    if max_pages and pages >= max_pages:
                        break
                except Exception as e:
                    continue
        
        print(f'Scraped {len(all_ids)} ids total.')
        print(all_ids)
        return all_ids


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawls over PolitTweet.org to query a twitter handle and extract its id.')
    parser.add_argument('handle_file', type=str, help='CSV file with Twitter\'s handle.')
    parser.add_argument('outputname', type=str, help='The name of the file to output.')
    parser.add_argument('--max_pages', type=int, help='The total amount of pages to scrape, if not all.', default=None)
    args = parser.parse_args()

    ids = scrape_polititweet(args.handle_file, max_pages=args.max_pages)

    df = pd.DataFrame(ids)
    df.to_csv(args.outputname, index=False)
