import os
import pandas as pd
import pytest
from unittest.mock import patch
from clean_vix import clean_vix_data

# filepath: src/test_clean_vix.py

@pytest.fixture
def mock_input_file(tmp_path):
    file_path = tmp_path / "input.csv"
    data = {
        "DATE": ["01/01/2023", "01/02/2023"],
        "OPEN": [20.0, 21.0],
        "HIGH": [22.0, 23.0],
        "LOW": [19.0, 20.0],
        "CLOSE": [21.0, 22.0],
    }
    pd.DataFrame(data).to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def mock_output_file(tmp_path):
    return tmp_path / "output.csv"

def test_clean_vix_data_success(mock_input_file, mock_output_file):
    clean_vix_data(mock_input_file, mock_output_file)
    df = pd.read_csv(mock_output_file)
    assert "AVG VIX" in df.columns
    assert "OPEN" not in df.columns
    assert "HIGH" not in df.columns
    assert "LOW" not in df.columns
    assert df["DATE"].iloc[0] == "1/1/23"

def test_clean_vix_data_empty_file(tmp_path, mock_output_file):
    file_path = tmp_path / "empty.csv"
    pd.DataFrame().to_csv(file_path, index=False)
    with pytest.raises(pd.errors.EmptyDataError):
        clean_vix_data(file_path, mock_output_file)

