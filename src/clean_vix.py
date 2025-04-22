#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gets VIX data extracted from Makefile and cleans it up.
"""
import argparse
import pandas as pd

def clean_vix_data(input_file, output_file):
    """
    Cleans the VIX data by removing unnecessary columns and renaming others.
    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output cleaned CSV file.
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Rename columns
    df.rename(columns={'CLOSE': 'AVG VIX'}, inplace=True)

    # Remove unnecessary columns
    df.drop(columns=['OPEN', 'HIGH', 'LOW'], inplace=True)

    # Format the date to 'm/d/yy'
    df['DATE'] = pd.to_datetime(df['DATE'], format='%m/%d/%Y')
    df['DATE'] = df['DATE'].dt.strftime('%-m/%-d/%y')

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cleans up VIX file.')
    parser.add_argument(
        'input_file',
        type=str,
        help='VIX raw CSV file.')
    parser.add_argument(
        'output_file',
        type=str,
        help='The name of the cleaned up VIX CSV file.')
    args = parser.parse_args()

    clean_vix_data(args.input_file, args.output_file)
