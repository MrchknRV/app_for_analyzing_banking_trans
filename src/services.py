import json
import logging

import pandas as pd

from config import PATH

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH / "logs" / "logging.log", "w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] - %(name)r - (%(filename)s).%(funcName)s:%(lineno)-3d - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


# simple_search
def simple_search_by_string(data: pd.DataFrame, search_string: str) -> str:
    logger.info("Запуск функции %s со строкой для поиска: %s", simple_search_by_string.__name__, search_string)
    """Функция ищет транзакции по строке в описании или категории и возвращает JSON-ответ."""
    try:
        required_data = {"Дата операции", "Номер карты", "Сумма операции", "Категория", "Описание"}
        logger.debug("Проверка файла на содержание колонок: %s", required_data)
        if not required_data.issubset(data.columns):
            missing = required_data - set(data.columns)
            logger.error("В файле отсутствуют необходимые колонки: %s", missing)
            raise ValueError(f"В файле отсутствуют необходимые колонки: {missing}")
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        logger.info("Фильтрация данных")
        found_data = data[
            (data["Описание"]).str.contains(search_string, case=False, na=False)
            | (data["Категория"]).str.contains(search_string, case=False, na=False)
        ]

        operations = []
        for _, row in found_data.iterrows():
            operations.append(
                {
                    "date": row["Дата операции"].strftime("%d.%m.%Y"),
                    "cards": row["Номер карты"][1:] if not pd.isna(row["Номер карты"]) else "Нет данных",
                    "amount": float(row["Сумма операции"]),
                    "category": row["Категория"],
                    "description": row["Описание"],
                }
            )

        result = {"count": len(found_data), "operations": operations}
        logger.info("Результат функции %s успешен", simple_search_by_string.__name__)
        return json.dumps(result, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        logger.error("Произошла ошибка: Файл не найден")
        return json.dumps({"ERROR": "Файл не найден"}, ensure_ascii=False)
    except Exception as ex:
        logger.error("Произошла ошибка: %s", ex)
        return json.dumps({"ERROR": f"Произошла ошибка: {str(ex)}"}, ensure_ascii=False)
