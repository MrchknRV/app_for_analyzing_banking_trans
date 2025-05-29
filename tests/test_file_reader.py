from unittest.mock import patch

import pandas as pd

from src.file_reader import reader_file_xlsx


def test_successful_read_file(valid_excel_data) -> None:
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = valid_excel_data

        result = reader_file_xlsx("test.xlsx")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Сумма операции" in result.columns
        assert result["Сумма операции"].iloc[1] == 200.75
        mock_read.assert_called_once_with("test.xlsx", engine="openpyxl")


def test_file_not_found() -> None:
    with patch("pandas.read_excel") as mock_read:
        mock_read.side_effect = FileNotFoundError("File not found")

        result = reader_file_xlsx("test.xlsx")
        assert result == []
        mock_read.assert_called_once_with("test.xlsx", engine="openpyxl")


def test_invalid_excel_data() -> None:
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = pd.DataFrame()  # Пустой DataFrame

        result = reader_file_xlsx("test.xlsx")
        assert result == []


def test_excel_read_error() -> None:
    with patch("pandas.read_excel") as mock_read:
        mock_read.side_effect = Exception("Read error")

        result = reader_file_xlsx("test.xlsx")
        assert result == []


def test_empty_dataframe() -> None:
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = pd.DataFrame(columns=["Сумма операции", "Категория"])

        result = reader_file_xlsx("test.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
