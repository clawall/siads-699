import pandas as pd
import pytest
from unittest.mock import patch
from split_large_files import split_large_files, estimate_bytes_per_row

@pytest.fixture
def setup_test_environment(tmp_path):
    # Create a temporary directory and files for testing
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()

    # Create a large CSV file
    large_csv_path = test_dir / "large_file.csv"
    small_csv_path = test_dir / "small_file.csv"

    large_df = pd.DataFrame({"col1": range(100000), "col2": range(100000)})
    small_df = pd.DataFrame({"col1": range(10), "col2": range(10)})

    large_df.to_csv(large_csv_path, index=False)
    small_df.to_csv(small_csv_path, index=False)

    return test_dir, large_csv_path, small_csv_path

def test_estimate_bytes_per_row():
    # Test the estimate_bytes_per_row function
    sample_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    bytes_per_row = estimate_bytes_per_row(sample_df)
    assert bytes_per_row > 0

def test_split_large_files_splits_large_file(setup_test_environment):
    test_dir, large_csv_path, _ = setup_test_environment

    # Run the split_large_files function
    split_large_files(str(test_dir), max_file_size=1024 * 1024)  # 1 MB

    # Check that the large file was split into chunks
    chunk_files = list(test_dir.glob("large_file__*.csv"))
    assert len(chunk_files) > 0

    # Check that the original file was removed
    assert not large_csv_path.exists()

def test_split_large_files_skips_small_file(setup_test_environment):
    test_dir, _, small_csv_path = setup_test_environment

    # Run the split_large_files function
    split_large_files(str(test_dir), max_file_size=1024 * 1024)  # 1 MB

    # Check that the small file was not split
    assert small_csv_path.exists()

def test_split_large_files_handles_non_csv_files(setup_test_environment):
    test_dir, _, _ = setup_test_environment

    # Create a non-CSV file
    non_csv_path = test_dir / "non_csv_file.txt"
    non_csv_path.write_text("This is a test file.")

    # Run the split_large_files function
    split_large_files(str(test_dir), max_file_size=1024 * 1024)  # 1 MB

    # Check that the non-CSV file was not removed or modified
    assert non_csv_path.exists()

@patch("os.remove")
def test_split_large_files_removes_original_file(mock_remove, setup_test_environment):
    test_dir, large_csv_path, _ = setup_test_environment

    # Run the split_large_files function
    split_large_files(str(test_dir), max_file_size=1024 * 1024)  # 1 MB

    # Check that os.remove was called for the original file
    mock_remove.assert_called_once_with(str(large_csv_path))

def test_split_large_files_handles_empty_folder(tmp_path):
    # Create an empty directory
    empty_dir = tmp_path / "empty_data"
    empty_dir.mkdir()

    # Run the split_large_files function
    split_large_files(str(empty_dir), max_file_size=1024 * 1024)  # 1 MB

    # Check that no files were created
    assert len(list(empty_dir.iterdir())) == 0