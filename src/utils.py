import json
import logging
from datetime import datetime
from typing import Any, Union

import pandas as pd
import requests

from config import JSON_PATH, PATH

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
        with open(JSON_PATH, "r", encoding="UTF-8") as f:
            logger.info('Данные успешно получены из %s', JSON_PATH)
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
        date_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
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
