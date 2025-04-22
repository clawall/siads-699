# Makefile

# Define the Python interpreter
PYTHON = python3

# Define the targets

all: ./data/03_raw_df.csv ./data/VIX1.csv

./data/02_handles.csv: ./src/convert_handles_to_ids.py
	$(PYTHON) ./src/convert_handles_to_ids.py ./data/01_influential_people.csv ./data/02_handles.csv

./data/tweets/.stamp: ./data/02_handles.csv ./src/read_tweets.py
	mkdir -p ./data/tweets
	$(PYTHON) ./src/read_tweets.py ./data/02_handles.csv ./data/tweets/
	touch ./data/tweets/.stamp

./data/tweets/.split_stamp: ./data/tweets/.stamp ./src/split_large_files.py
	mkdir -p ./data/tweets
	$(PYTHON) ./src/split_large_files.py ./data/tweets/
	touch ./data/tweets/.split_stamp

./data/03_raw_df.csv: ./data/tweets/.split_stamp ./src/clean.py
	$(PYTHON) ./src/clean.py ./data/tweets/ ./data/03_raw_df.csv
	@echo "Data processing complete. Output saved to ./data/03_raw_df.csv"
	@echo "You can now run the analysis script to analyze the data."

./data/taq/.stamp: ./data/taq_raw ./src/export_taq_to_parquet.py
	mkdir -p ./data/taq
	$(PYTHON) ./src/export_taq_to_parquet.py ./data/taq_raw ./data/taq/
	touch ./data/taq/.stamp

./data/VIX_raw.csv:
	curl -XGET https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv >> data/VIX_raw.csv

./data/VIX1.csv:  ./data/VIX_raw.csv ./src/clean_vix.py
	$(PYTHON) ./src/clean_vix.py ./data/VIX_raw.csv ./data/VIX1.csv
	@echo "VIX data processing complete. Output saved to ./data/VIX1.csv"
