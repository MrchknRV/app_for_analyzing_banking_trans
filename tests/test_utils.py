import json
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from src.utils import get_currency_rates, get_greeting, get_month_date_start_end, load_user_settings


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
