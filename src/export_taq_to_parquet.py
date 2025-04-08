import pandas as pd
import argparse
import os

def export_taq_to_parquet(input_folder, output_folder, chunksize=10**5, compression='snappy'):
    """
    Export CSV files to Parquet format.
    """
    results = []

    for filename in os.listdir(input_folder):
        if not filename.endswith('.csv'):
            continue

        print(f'Processing file: {filename}...')
        full_path = os.path.join(input_folder, filename)

        for chunk in pd.read_csv(full_path, chunksize=chunksize, dtype={
            'SYM_SUFFIX': str,
            'SYM_ROOT': str,
            'EX': str,
            'TR_SCOND': str
        }):
            chunk['timestamp'] = pd.to_datetime(chunk['DATE'] + ' ' + chunk['TIME_M'])
            
            chunk['PRICE'] = pd.to_numeric(chunk['PRICE'], errors='coerce')
            
            chunk = chunk[['timestamp', 'SYM_ROOT', 'PRICE']]

            chunk.set_index('timestamp', inplace=True)

            resampled = (
                chunk
                .groupby('SYM_ROOT')
                .resample('1min')
                .agg({'PRICE': 'mean'})
                .reset_index()
            )

            results.append(resampled)
        
        final = pd.concat(results)

        final = (
        final
            .groupby(['timestamp', 'SYM_ROOT'])['PRICE']
            .mean()
            .reset_index()
        )

        final = final.rename(columns={'PRICE': 'avg_price'})
        final['year'] = final['timestamp'].dt.year

        print(f'{filename} aggregated, persisting into Parquet...')
        final.to_parquet(
            output_folder,
            engine='pyarrow',
            index=False,
            compression=compression,
            partition_cols=['SYM_ROOT', 'year']
        )

        print(f'{filename} completed!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export TAQ CSVs in a folder to parquet files.')
    parser.add_argument('input_folder', type=str, help='Folder with all the CSV files.')
    parser.add_argument('output_folder', type=str, help='Output folder for Parquet files.')
    parser.add_argument('--chunksize', type=int, default=10**5, help='Number of rows per chunk to read.')
    parser.add_argument('--compression', type=str, default='snappy', help='Compression algorithm for Parquet files.')
    args = parser.parse_args()

    export_taq_to_parquet(args.input_folder, args.output_folder, args.chunksize, args.compression)
