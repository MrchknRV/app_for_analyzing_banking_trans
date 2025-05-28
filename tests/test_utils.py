import json
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import numpy as np
import pandas as pd
import pytest
import requests

from src.utils import (
    get_cards_data,
    get_currency_rates,
    get_filtered_operations,
    get_greeting,
    get_month_date_start_end,
    get_stock_prices,
    load_user_settings,
)


# Тесты для функц load_user)settings
@patch(
    "builtins.open",
    mock_open(read_data=json.dumps({"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]})),
)
@patch("config.JSON_PATH", "valid_path.json")  # Замените 'module' на имя вашего модуля
def test_successful_load() -> None:
    result = load_user_settings()
    assert result == {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}


def test_missing_file() -> None:
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_user_settings()
        assert result == {}


@patch("builtins.open", mock_open(read_data="{invalid json}"))
@patch("config.JSON_PATH", "invalid_path.json")
def test_invalid_json() -> None:
    result = load_user_settings()
    assert result == {}


@patch("builtins.open", side_effect=Exception("Error"))
@patch("config.JSON_PATH", "error_path.json")
def test_general_exception_handling(mock_open) -> None:
    result = load_user_settings()
    assert result == {}


# Тесты для функции get_greeting
@pytest.mark.parametrize(
    "test_inp, expected",
    [
        ("15.05.2023 08:30:00", "Доброе утро"),
        ("15.05.2023 14:15:00", "Добрый день"),
        ("15.05.2023 19:45:00", "Добрый вечер"),
        ("15.05.2023 03:20:00", "Доброй ночи"),
        ("15.05.2023 05:00:00", "Доброе утро"),
        ("15.05.2023 11:59:59", "Доброе утро"),
        ("15.05.2023 12:00:00", "Добрый день"),
        ("15.05.2023 16:59:59", "Добрый день"),
        ("15.05.2023 17:00:00", "Добрый вечер"),
        ("15.05.2023 23:59:59", "Добрый вечер"),
        ("15.05.2023 00:00:00", "Доброй ночи"),
        ("15.05.2023 04:59:59", "Доброй ночи"),
    ],
)
def test_get_greeting(test_inp: str, expected: str) -> None:
    assert get_greeting(test_inp) == expected


# Тесты для функции get_month_date_start_end
def test_valid_date_format() -> None:
    result = get_month_date_start_end("2023-05-15 14:30:45")
    assert len(result) == 2
    assert isinstance(result[0], datetime)
    assert isinstance(result[1], datetime)
    assert result[0].strftime("%Y-%m-%d %H:%M:%S") == "2023-05-01 00:00:00"
    assert result[1].strftime("%Y-%m-%d %H:%M:%S") == "2023-05-15 14:30:45"


def test_first_day_of_month() -> None:
    result = get_month_date_start_end("2023-05-01 00:00:00")
    assert result[0].strftime("%Y-%m-%d %H:%M:%S") == "2023-05-01 00:00:00"
    assert result[1].strftime("%Y-%m-%d %H:%M:%S") == "2023-05-01 00:00:00"


def test_year_february() -> None:
    result = get_month_date_start_end("2020-02-29 23:59:59")
    assert result[0].strftime("%Y-%m-%d") == "2020-02-01"
    assert result[1].strftime("%Y-%m-%d") == "2020-02-29"


def test_end_of_year() -> None:
    result = get_month_date_start_end("2023-12-31 23:59:59")
    assert result[0].strftime("%Y-%m-%d") == "2023-12-01"
    assert result[1].strftime("%Y-%m-%d") == "2023-12-31"


# Тесты функции get_currency_rates
@patch("requests.get")
def test_successful_response_with_valid_currencies(mock_get) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Valute": {"USD": {"Value": 75.50}, "EUR": {"Value": 85.25}, "GBP": {"Value": 95.75}}
    }
    mock_get.return_value = mock_response

    currencies = ["USD", "EUR", "GBP"]
    result = get_currency_rates(currencies)

    assert len(result) == 3
    assert {"currency": "USD", "rate": 75.50} == result[0]
    assert {"currency": "EUR", "rate": 85.25} == result[1]
    assert {"currency": "GBP", "rate": 95.75} == result[2]
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


@patch("requests.get")
def test_response_with_mixed_currencies(mock_get) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 75.50}, "EUR": {"Value": 85.25}}}
    mock_get.return_value = mock_response

    currencies = ["USD", "EUR", "JPY"]
    result = get_currency_rates(currencies)

    assert len(result) == 3
    assert {"currency": "USD", "rate": 75.50} == result[0]
    assert {"currency": "EUR", "rate": 85.25} == result[1]
    assert {"currency": "JPY", "rate": "Нет данных"} == result[2]


@patch("requests.get")
def test_non_200_response(mock_get) -> None:
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    currencies = ["USD", "EUR"]
    result = get_currency_rates(currencies)

    assert result == "Не успешный запрос.\nКод ошибки: 404."


@patch("requests.get", side_effect=requests.exceptions.ConnectionError)
def test_connection_error(mock_get) -> None:
    currencies = ["USD", "EUR"]
    result = get_currency_rates(currencies)

    assert result == []


@patch("requests.get", side_effect=requests.exceptions.Timeout)
def test_timeout_error(mock_get) -> None:
    currencies = ["USD"]
    result = get_currency_rates(currencies)

    assert result == []


@patch("requests.get")
def test_json_decode_error(mock_get) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    currencies = ["USD"]
    result = get_currency_rates(currencies)

    assert result == []


# Тесты для функции get_stock_prices
@patch("requests.get")
def test_successful_stock_prices(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Global Quote": {"05. price": "175.50"}}
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"], api_key="test_key")
    assert result == [{"stock": "AAPL", "price": "175.50"}]
    mock_get.assert_called_once_with(
        "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=test_key"
    )


@patch("requests.get")
def test_multiple_stocks(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"Global Quote": {"05. price": "175.50"}},
        {"Global Quote": {"05. price": "325.45"}},
    ]
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL", "MSFT"], api_key="test_key")
    assert result == [{"stock": "AAPL", "price": "175.50"}, {"stock": "MSFT", "price": "325.45"}]


@patch("requests.get")
def test_request_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"], api_key="test_key")
    assert result == "Не успешный запрос.\nКод ошибки: 404."


@patch("requests.get", side_effect=requests.exceptions.RequestException)
def test_request_exception(mock_get):
    result = get_stock_prices(["AAPL"], api_key="test_key")
    assert result == [{"stock": "AAPL", "price": "Нет данных"}]


@patch("requests.get")
def test_no_api_key(mock_get):
    get_stock_prices(["AAPL"])
    mock_get.assert_called_once_with("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=None")


def test_empty_stocks_list():
    result = get_stock_prices([])
    assert result == []


# Тесты для фукнции get_filtered_operations
def test_successful_filter(sample_data):
    date = "2021-12-29 19:06:39"
    result = get_filtered_operations(sample_data, date)

    assert len(result) == 4
    assert isinstance(result, pd.DataFrame)


def test_filter_empty_result(sample_data):
    result = get_filtered_operations(sample_data, "2022-01-01")

    assert len(result) == 0
    assert isinstance(result, pd.DataFrame)


def test_invalid_date_format(sample_data):
    invalid_date = "2021/12"

    result = get_filtered_operations(sample_data, invalid_date)
    assert len(result) == 0


def test_filter_with_empty_data():
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория"])
    result = get_filtered_operations(empty_df, "2021-12")

    # Проверяем, что возвращен пустой DataFrame
    assert len(result) == 0
    assert isinstance(result, pd.DataFrame)


# Тесты для функции get_cards_data
def test_get_cards_data_successful(sample_data):
    result = get_cards_data(sample_data)
    assert len(result) == 3
    assert result == [
        {"last_digits": "7197", "total_spent": -79.37, "cashback": -1.0},
        {"last_digits": "5091", "total_spent": -21511.6, "cashback": -216.0},
        {"last_digits": "4556", "total_spent": -670.0, "cashback": -7.0},
    ]
    assert isinstance(result, list)


def test_get_cards_data_empty():
    empty_df = pd.DataFrame(columns=["Номер карты", "Сумма операции"])
    result = get_cards_data(empty_df)
    assert result == []


def test_get_cards_data_with_nan():
    nan_df = pd.DataFrame({"Номер карты": [np.nan, np.nan], "Сумма операции": [100, 200]})
    result = get_cards_data(nan_df)
    assert result == []


def test_get_cards_data_exception_handling(monkeypatch):
    def mock_unique(*args, **kwargs):
        raise Exception("error")

    monkeypatch.setattr(pd.Series, "unique", mock_unique)

    test_df = pd.DataFrame({"Номер карты": ["*7197"], "Сумма операции": [100]})
    result = get_cards_data(test_df)

    assert isinstance(result, pd.DataFrame)
    assert result.equals(test_df)
