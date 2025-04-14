import os
import pandas as pd
import pytest
from unittest.mock import patch
from export_taq_to_parquet import export_taq_to_parquet

@pytest.fixture
def mock_input_folder(tmp_path):
    folder = tmp_path / "input"
    folder.mkdir()
    return folder

@pytest.fixture
def mock_output_folder(tmp_path):
    folder = tmp_path / "output"
    folder.mkdir()
    return folder

@pytest.fixture
def mock_csv_file(mock_input_folder):
    file_path = mock_input_folder / "test.csv"
    data = {
        "DATE": ["2023-01-01", "2023-01-01"],
        "TIME_M": ["12:00:00", "12:01:00"],
        "SYM_ROOT": ["AAPL", "AAPL"],
        "PRICE": [150.0, 151.0],
    }
    pd.DataFrame(data).to_csv(file_path, index=False)
    return file_path

def test_export_taq_to_parquet_success(mock_input_folder, mock_output_folder, mock_csv_file):
    export_taq_to_parquet(
        input_folder=mock_input_folder,
        output_folder=mock_output_folder,
        chunksize=10**5,
        compression='snappy'
    )
    assert len(os.listdir(mock_output_folder)) > 0

def test_export_taq_to_parquet_no_csv_files(mock_input_folder, mock_output_folder):
    export_taq_to_parquet(
        input_folder=mock_input_folder,
        output_folder=mock_output_folder,
        chunksize=10**5,
        compression='snappy'
    )
    assert len(os.listdir(mock_output_folder)) == 0

@patch("export_taq_to_parquet.pd.read_csv")
def test_export_taq_to_parquet_read_csv_error(mock_read_csv, mock_input_folder, mock_output_folder, mock_csv_file):
    mock_read_csv.side_effect = Exception("Error reading CSV")
    with pytest.raises(Exception, match="Error reading CSV"):
        export_taq_to_parquet(
            input_folder=mock_input_folder,
            output_folder=mock_output_folder,
            chunksize=10**5,
            compression='snappy'
        )
