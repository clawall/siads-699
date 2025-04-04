import argparse
import pandas as pd
import os
from glob import glob

def merge_csv_files(tweet_input_folder, output_file):
    csv_files = glob(os.path.join(tweet_input_folder, '*.csv'))

    df_list = []
    for file in csv_files:
        if not os.path.isfile(file):
            print(f"File {file} does not exist.")
            continue
        
        if not file.endswith('.csv'):
            print(f"File {file} is not a CSV file.")
            continue

        if os.path.getsize(file) < 10:
            print(f"File {file} is empty.")
            continue

        print(f"Processing file {file}...")
        df_list.append(pd.read_csv(file, low_memory=False))
    
    merged_df = pd.concat(df_list, ignore_index=True)

    merged_df.to_csv(os.path.join(output_file), index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge tweets files.')
    parser.add_argument('tweet_input_folder', type=str, help='Folder with all the tweets files.')
    parser.add_argument('output_file', type=str, help='The name of the merged CSV file.')
    args = parser.parse_args()

    merge_csv_files(args.tweet_input_folder, args.output_file)