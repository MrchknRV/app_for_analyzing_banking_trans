from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.reports import log_report, spending_by_category


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_log_report_decorator(mock_json_dump, mock_file, sample_data) -> None:
    @log_report(filename="test_report.json")
    def test_func():
        return sample_data

    result = test_func()

    assert result.equals(sample_data)
    mock_file.assert_called_once()
    mock_json_dump.assert_called_once()


def test_log_report_decorator_not_dataframe():
    @log_report(filename="test_report.json")
    def test_func():
        return "not a dataframe"

    with patch("builtins.open", new_callable=mock_open) as mock_file:
        result = test_func()

        mock_file.assert_not_called()
        assert result == "not a dataframe"


def test_spending_success(sample_data: pd.DataFrame) -> None:
    result = spending_by_category(sample_data, "Фастфуд", "2021-12-31 12:12:12")

    assert isinstance(result, pd.DataFrame)
    assert result.loc[0, "total_expenses"] == -1446.4
    assert result.loc[0, "date_from"] == "02.10.2021"
    assert result.loc[0, "date_to"] == "31.12.2021"


def test_missing_columns() -> None:
    missing_columns_data = {"Дата операции": datetime(2021, 11, 7), "Номер карты": "*3456", "Категория": "TEST"}

    with pytest.raises(TypeError) as ex_info:
        spending_by_category(missing_columns_data)
        assert ex_info.value == "В файле отсутствуют необходимые колонки: Сумма операции"


def test_spending_missing_category(sample_data: pd.DataFrame) -> None:
    result = spending_by_category(sample_data, "Канцтовары", "2021-12-31")

    assert isinstance(result, pd.DataFrame)
    assert result.loc[0, "total_expenses"] == 0


def test_spending_by_category_default_date(sample_data: pd.DataFrame) -> None:
    with freeze_time("2021-12-31 12:12:12"):
        result = spending_by_category(sample_data, "Фастфуд")

        assert isinstance(result, pd.DataFrame)
        assert result.loc[0, "date_to"] == "31.12.2021"
        assert result.loc[0, "date_from"] == "02.10.2021"
