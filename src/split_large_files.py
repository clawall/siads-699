import pandas as pd
import argparse
import os


DEFAULT_MAX_FILE_SIZE = 45 * 1024 * 1024  # 95 MB

# Helper: estimate bytes per row from sampling
def estimate_bytes_per_row(sample_df):
    csv_sample = sample_df.to_csv(index=False).encode('utf-8')
    return len(csv_sample) / len(sample_df)

def split_large_files(input_folder, max_file_size):
    for filename in os.listdir(input_folder):
        if not filename.endswith('.csv'):
            continue

        full_path = os.path.join(input_folder, filename)
        file_size = os.path.getsize(full_path)

        if file_size <= max_file_size:
            print(f'Skipping {filename} (size OK: {file_size} bytes)')
            continue

        print(f'Splitting {filename} (size: {file_size} bytes)...')

        sample_df = pd.read_csv(full_path, nrows=100)
        bytes_per_row = estimate_bytes_per_row(sample_df)
        chunk_size = int(max_file_size / bytes_per_row)

        reader = pd.read_csv(full_path, chunksize=chunk_size)
        base_name = filename[:-4]

        for i, chunk in enumerate(reader):
            chunk_filename = f'{base_name}__{i}.csv'
            chunk_path = os.path.join(input_folder, chunk_filename)
            chunk.to_csv(chunk_path, index=False)
            print(f'  ➤ Wrote: {chunk_filename} ({chunk.shape[0]} rows)')

        os.remove(full_path)
        print(f'  ⛔ Removed original: {filename}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Splits tweet files into smaller chunks.')
    parser.add_argument('tweet_input_folder', type=str, help='Folder with all the tweets files.')
    parser.add_argument('--max_file_size', type=str, help='The max size for each CSV file.', default=DEFAULT_MAX_FILE_SIZE)
    args = parser.parse_args()

    split_large_files(args.tweet_input_folder, args.max_file_size)
