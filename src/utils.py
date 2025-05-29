import json
import logging
from datetime import datetime
from typing import Any, Union

import pandas as pd
import requests

from config import PATH

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH / "logs" / "logging.log", "w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] - %(name)r - (%(filename)s).%(funcName)s:%(lineno)-3d - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


# Загрузка настроек
def load_user_settings() -> dict:
    """Загружает пользовательские настройки из JSON-файла."""
    logger.info("Запуск функции %s", load_user_settings.__name__)
    try:
        logger.info("Получение данных из 'user_settings.json'")
        with open(PATH / "user_settings.json", "r", encoding="UTF-8") as f:
            logger.info("Данные успешно получены")
            return json.load(f)
    except Exception as ex:
        logger.error("Ошибка загрузки %s", ex)
        return {}


def get_greeting(date_str: str) -> str:
    """Функция анализирует переданную дату и возвращает соответствующее приветствие
    (утро, день, вечер или ночь). Если дата в неверном формате, используется текущее время."""
    logger.info("Запуск функции %s с значением %s", get_greeting.__name__, date_str)
    try:
        logger.info("Получение даты")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error("Неверный формат даты, используется текущая дата")
        date_obj = datetime.now()

    if 5 <= date_obj.hour < 12:
        return "Доброе утро"
    elif 12 <= date_obj.hour < 17:
        return "Добрый день"
    elif 17 <= date_obj.hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_month_date_start_end(date_str: str) -> Any:
    """Возвращает начало месяца и указанную дату. Если неверная дата, возвращает текущую"""
    logger.info("Запуск функции %s с значением %s", get_month_date_start_end.__name__, date_str)
    try:
        logger.info("Получение даты")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        month_start_obj = date_obj.replace(day=1, minute=0, hour=0, second=0)
        return month_start_obj, date_obj
    except ValueError:
        logger.error("Неверный формат даты, используется текущая дата")
        date_obj = datetime.now()
        month_start_obj = date_obj.replace(day=1, minute=0, hour=0, second=0)
        return month_start_obj.strftime("%d.%m.%Y"), date_obj.strftime("%d.%m.%Y")


def get_currency_rates(currencies: list) -> Union[list, str]:
    """Функция делает запрос к публичному API Центробанка России для получения
    актуальных курсов валют. Для каждого запрошенного кода валюты возвращает
    текущий курс или сообщение об отсутствии данных."""
    logger.info("Запуск функции %s с значением %s", get_currency_rates.__name__, currencies)
    rates = []
    try:
        logger.info("Обращение к Api")
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        status_code = response.status_code
        logger.info("Проверка статус-ответа")
        if status_code == 200:
            data = response.json()
            logger.info("Обращение успешно")
            for currency in currencies:
                if currency in data["Valute"]:
                    rate = data["Valute"][currency]["Value"]
                    rates.append({"currency": currency, "rate": rate})
                else:
                    rates.append({"currency": currency, "rate": "Нет данных"})
        else:
            logger.warning("Не успешный запрос.\nКод ошибки: %s.", status_code)
            return f"Не успешный запрос.\nКод ошибки: {status_code}."
    except Exception as ex:
        logger.error("Ошибка получения курса валют: %s", ex)
    return rates


def get_stock_prices(stocks: list, api_key=None) -> Any:
    """Функция делает запросы к API Alpha Vantage для получения текущих цен
    указанных акций. Для каждой акции возвращает последнюю известную цену."""
    logger.info("Запуск функции %s с значением %s", get_stock_prices.__name__, stocks)
    prices = []
    for stock in stocks:
        logger.info(f"Запрос цены для акции: {stock}")
        try:
            logger.info("Обращение к Api")
            response = requests.get(
                f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            )
            if response.status_code != 200:
                logger.error("Ошибка запроса для %s. Код: %d", stock, response.status_code)
                prices.append({"stock": stock, "price": "Нет данных"})
                continue

            data = response.json()
            if "Global Quote" not in data or "05. price" not in data["Global Quote"]:
                logger.error("Неверная структура ответа для %s", stock)
                prices.append({"stock": stock, "price": "Нет данных"})
                continue

            try:
                price = float(data["Global Quote"]["05. price"])
                prices.append({"stock": stock, "price": price})
                logger.info("Успешно получена цена для %s: %.2f", stock, price)
            except (ValueError, TypeError) as ex:
                logger.error("Ошибка преобразования цены для %s: %s", stock, ex)
                prices.append({"stock": stock, "price": "Нет данных"})

        except requests.RequestException as ex:
            logger.error(f"Ошибка при получении цены для {stock}: {ex}")
            prices.append({"stock": stock, "price": "Нет данных"})
    return prices


def get_filtered_operations(data: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Функция принимает DataFrame с операциями и строку с датой, возвращает отфильтрованный
    DataFrame, содержащий только операции за указанный месяц."""
    logger.info("Запуск функции %s", get_filtered_operations.__name__)
    try:
        date_start, date_end = get_month_date_start_end(date_str)
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_df = data[(data["Дата операции"] >= date_start) & (data["Дата операции"] <= date_end)]
        return filtered_df
    except Exception as ex:
        logging.error("Ошибка фильтрации: %s. Возврат данных", ex)
        return data


def get_cards_data(data: pd.DataFrame) -> Union[list, pd.DataFrame]:
    """Агрегирует данные по банковским картам из DataFrame, вычисляя общие траты и кэшбэк.
    Обрабатывает DataFrame с транзакциями, группирует операции по номерам карт (игнорируя NaN),
    и возвращает список словарей с информацией по каждой карте: последние цифры номера,
    суммарные траты и рассчитанный кэшбэк"""
    logger.info("Запуск функции %s", get_cards_data.__name__)
    try:
        logger.info("Получение данных")
        cards = []
        for card in data["Номер карты"].unique():
            if pd.isna(card):
                continue
            last_digits = card[1:]
            card_data = data[data["Номер карты"] == card]
            total_spent = card_data["Сумма операции"].sum()
            cashback = total_spent // 100
            cards.append(
                {
                    "last_digits": last_digits,
                    "total_spent": float(round(total_spent, 2)),
                    "cashback": float(round(cashback, 2)),
                }
            )
            logger.info("Данные получены")
        return cards
    except Exception as ex:
        logging.error("Ошибка получения данных: %s. Возврат данных", ex)
        return data


def get_top_transactions(data, quant=5):
    logger.info("Запуск функции %s", get_top_transactions.__name__)
    try:
        logger.info("Получение данных")
        top_data = data.nlargest(quant, "Сумма операции")
        top_operations = []
        for _, row in top_data.iterrows():
            top_operations.append(
                {
                    "date": row["Дата операции"].strftime("%d.%m.%Y"),
                    "amount": round(row["Сумма операции"], 2),
                    "category": row["Категория"],
                    "description": row["Описание"],
                }
            )
            logger.info("Данные получены")
        return top_operations
    except Exception as ex:
        logging.error("Ошибка получения данных: %s", ex)
        return []
