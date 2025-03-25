# Makefile

# Define the Python interpreter
PYTHON = python3

# Define the targets
all: ./data/03_raw_df.csv

./data/02_handles.csv: ./src/convert_handles_to_ids.py
	$(PYTHON) ./src/convert_handles_to_ids.py ./data/01_influential_people.csv ./data/02_handles.csv

./data/03_raw_df.csv: ./data/02_handles.csv ./src/read_tweets.py
	$(PYTHON) ./src/read_tweets.py ./data/02_handles.csv ./data/03_raw_df.csv
