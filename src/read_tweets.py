#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script scrapes tweets from the Polititweet website.
It extracts tweets from a specific Twitter account and saves them to CSV files.
The script uses BeautifulSoup for HTML parsing and requests for HTTP requests.
It is designed to be run from the command line with the following arguments:
1. account_id_file: Path to the CSV file containing Twitter account IDs.
2. output_folder: Path to the folder where the output CSV files will be saved.
3. max_pages (optional): The maximum number of pages to scrape for each account.
"""
import argparse
import csv
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests

SLEEP_TIMEOUT_SECONDS = .1
BASE_URL = 'https://polititweet.org'


def extract_tweet_data(soup):
    """
    Extracts tweet data from the soup object.
    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML of the page.
    Returns:
        list: A list of dictionaries containing tweet data.
    """
    # 1. Find main tweets grid
    tweets_grid = soup.find('div', {'class': 'grid'})

    if not tweets_grid:
        print('Could not find the tweets grid on page.')
        return None

    # 2. Extract tweets from the anchor tags, which are the tweet cards.
    tweet_cards = tweets_grid.find_all('a', {'class': 'box tweet-card'})
    if not tweet_cards:
        print('Could not find the tweet cards on the grid.')
        return None

    all_tweets = []

    for element in tweet_cards:
        tweet_data = {}

        tweet = requests.get(
            f'{BASE_URL}{element.get("href")}&raw=True',
            timeout=10)
        if tweet.status_code != 200:
            print(f'Failed to retrieve tweet: status {tweet.status_code}')
            continue
        tweet_data = tweet.json()

        all_tweets.append(tweet_data)

    return all_tweets


def scrape_page(url):
    """
    Scrapes a single page of tweets from the given URL.
    Args:
        url (str): The URL of the page to scrape.
    Returns:
        list: A list of dictionaries containing tweet data.
        str: The URL for the next page, if available.
    """
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print(f'Failed to retrieve {url}: status {response.status_code}')
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    page_tweets = extract_tweet_data(soup)

    next_link = soup.find('a', {'class': 'pagination-next'}, string='Next')

    return page_tweets, next_link.get('href') if next_link else None


def scrape_polititweet(account_id, max_pages=None):
    """
    Scrapes tweets from a specific account on Polititweet.
    Args:
        account_id (str): The Twitter account ID to scrape.
        max_pages (int): The maximum number of pages to scrape.
    Returns:
        list: A list of dictionaries containing tweet data.
    """
    pages = 0
    all_tweets = []
    next_url = f'?account={account_id}'

    while next_url:
        print(f'Scraping page {next_url}...')
        try:
            page_tweets, next_url = scrape_page(f'{BASE_URL}/tweets{next_url}')

            all_tweets.extend(page_tweets)
        except requests.exceptions.RequestException as e:
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
    """"
    Scrapes tweets from multiple accounts listed in a CSV file.
    Args:
        account_id_file (str): Path to the CSV file containing Twitter account IDs.
        output_folder (str): Path to the folder where the output CSV files will be saved.
        max_pages (int): The maximum number of pages to scrape for each account.
    """
    with open(account_id_file, 'r', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header

        for account_ids in reader:
            account_id = account_ids[0]
            tweets = scrape_polititweet(account_id, max_pages=max_pages)
            df = pd.DataFrame(tweets)
            df.to_csv(f'{output_folder}/{account_id}.csv', index=False)

            # Delay to be kind to the server
            time.sleep(SLEEP_TIMEOUT_SECONDS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Crawls over PolitTweet.org to query tweets from a person.')
    parser.add_argument(
        'account_id_file',
        type=str,
        help='File containg Twitter\'s account ID to scrape.')
    parser.add_argument(
        'output_folder',
        type=str,
        help='The name of the folder to output CSV files.')
    parser.add_argument(
        '--max_pages',
        type=int,
        help='The total amount of pages to scrape, if not all.',
        default=None)
    args = parser.parse_args()

    scrape_all_tweets(
        args.account_id_file,
        args.output_folder,
        max_pages=args.max_pages)
