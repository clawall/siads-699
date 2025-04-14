import unittest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from clean import merge_csv_files

class TestMergeCSVFiles(unittest.TestCase):

    @patch('clean.glob')
    @patch('clean.os.path.isfile')
    @patch('clean.os.path.getsize')
    @patch('clean.pd.read_csv')
    @patch('clean.pd.DataFrame.to_csv')
    def test_merge_csv_files_success(self, mock_to_csv, mock_read_csv, mock_getsize, mock_isfile, mock_glob):
        # Mock the CSV files in the folder
        mock_glob.return_value = ['file1.csv', 'file2.csv']
        mock_isfile.return_value = True
        mock_getsize.return_value = 100
        mock_read_csv.side_effect = [
            pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
        ]

        # Call the function
        merge_csv_files('input_folder', 'output.csv')

        # Assert that the files were read and merged
        mock_read_csv.assert_any_call('file1.csv', low_memory=False)
        mock_read_csv.assert_any_call('file2.csv', low_memory=False)
        self.assertEqual(mock_read_csv.call_count, 2)
        mock_to_csv.assert_called_once_with('output.csv', index=False)

    @patch('clean.glob')
    @patch('clean.os.path.isfile')
    @patch('clean.os.path.getsize')
    def test_merge_csv_files_empty_folder(self, mock_getsize, mock_isfile, mock_glob):
        # Mock an empty folder
        mock_glob.return_value = []

        # Call the function
        with self.assertRaises(ValueError):
            merge_csv_files('input_folder', 'output.csv')

    @patch('clean.glob')
    @patch('clean.os.path.isfile')
    @patch('clean.os.path.getsize')
    def test_merge_csv_files_non_csv_files(self, mock_getsize, mock_isfile, mock_glob):
        # Mock files that are not CSV
        mock_glob.return_value = ['file1.txt', 'file2.doc']
        mock_isfile.return_value = True

        # Call the function
        with self.assertRaises(ValueError):
            merge_csv_files('input_folder', 'output.csv')

    @patch('clean.glob')
    @patch('clean.os.path.isfile')
    @patch('clean.os.path.getsize')
    def test_merge_csv_files_empty_csv(self, mock_getsize, mock_isfile, mock_glob):
        # Mock an empty CSV file
        mock_glob.return_value = ['file1.csv']
        mock_isfile.return_value = True
        mock_getsize.return_value = 0

        # Call the function
        with self.assertRaises(ValueError):
            merge_csv_files('input_folder', 'output.csv')

    @patch('clean.glob')
    @patch('clean.os.path.isfile')
    @patch('clean.os.path.getsize')
    @patch('clean.pd.read_csv')
    def test_merge_csv_files_partial_failures(self, mock_read_csv, mock_getsize, mock_isfile, mock_glob):
        # Mock files with one valid and one invalid CSV
        mock_glob.return_value = ['file1.csv', 'file2.csv']
        mock_isfile.side_effect = [True, True]
        mock_getsize.side_effect = [100, 0]
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

        # Call the function
        merge_csv_files('input_folder', 'output.csv')

        # Assert that only the valid file was processed
        mock_read_csv.assert_called_once_with('file1.csv', low_memory=False)

if __name__ == '__main__':
    unittest.main()