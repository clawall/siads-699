#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert Twitter handles to Twitter IDs using Polititweet.org
"""
import argparse
import csv
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests

BASE_URL = 'https://polititweet.org/figures'


def extract_twitter_id(handle, soup):
    """
    Extracts the Twitter ID from the Polititweet page for a given handle.
    Args:
        handle (str): The Twitter handle to search for.
        soup (BeautifulSoup): The BeautifulSoup object containing the page content.
    Returns:
        str: The Twitter ID if found, otherwise None.
    """
    # 1. Find main tweets grid
    tweets_grid = soup.find('div', {'class': 'grid'})

    if not tweets_grid:
        print('...NOT FOUND!')
        return None

    # 2. Extract ids from the anchor tags, which are the tweet cards.
    figure_cards = tweets_grid.find_all('a', {'class': 'box figure-card'})
    if not figure_cards:
        print('...NOT FOUND!')
        return None

    for element in figure_cards:
        user_handle = element.find('span', href=True)['href'].split('/')[-1]

        if user_handle == handle:
            figure_url = element['href'].split('=')[-1]
            print(f'...FOUND! {figure_url}')
            return figure_url

    return None


def scrape_page(url, handle):
    """
    Scrapes a single page of Polititweet for a given Twitter handle.
    Args:
        url (str): The URL of the page to scrape.
        handle (str): The Twitter handle to search for.
    Returns:
        tuple: A tuple containing the Twitter ID and the next URL to scrape.
    """
    response = requests.get(url, timeout=10)

    response.raise_for_status()  # Raise an error for bad responses

    soup = BeautifulSoup(response.text, 'html.parser')

    handle_id = extract_twitter_id(handle, soup)

    if not handle_id:
        return None, soup.find(
            'a:not([disabled])', {
                'class': 'pagination-next'}, string='Next')

    return handle_id, None


def scrape_polititweet(handle_file):
    """
    Scrapes Polititweet for Twitter handles and extracts their IDs.
    Args:
        handle_file (str): The path to the CSV file containing Twitter handles.
    Returns:
        list: A list of dictionaries containing Twitter handles and their corresponding IDs.
    """
    with open(handle_file, 'r', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)

        all_ids = []
        for handles in reader:
            handle = handles[0]
            print(f'Scraping page for {handle}...', end='')
            pages = 0
            next_url = f'?search={handle}'

            while next_url:
                try:
                    handle_id, next_url = scrape_page(
                        f'{BASE_URL}{next_url}', handle)

                    if handle_id:
                        all_ids.append({'id': handle_id, 'handle': handle})
                        break

                    # Delay to be kind to the server
                    time.sleep(.1)

                    pages += 1
                except requests.exceptions.RequestException:
                    continue

        print(f'Scraped {len(all_ids)} ids total.')
        print(all_ids)
        return all_ids


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Crawls over PolitTweet.org to query a twitter handle and extract its id.')
    parser.add_argument(
        'handle_file',
        type=str,
        help='CSV file with Twitter\'s handle.')
    parser.add_argument(
        'outputname',
        type=str,
        help='The name of the file to output.')

    args = parser.parse_args()

    ids = scrape_polititweet(args.handle_file)

    df = pd.DataFrame(ids)
    df.to_csv(args.outputname, index=False)
