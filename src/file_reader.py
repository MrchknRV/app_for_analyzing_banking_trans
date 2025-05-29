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


def reader_file_xlsx(pathfile: str):
    """Функция для считывания финансовых операций из Excel"""
    logger.info("Запуск функции %s", reader_file_xlsx.__name__)
    try:
        logger.info("Считываем данные из файла %s", pathfile)
        df = pd.read_excel(pathfile, engine="openpyxl")
        df["Сумма операции"] = df["Сумма операции"].astype(float).abs()
        logger.info("Функция %s успешно завершилась", reader_file_xlsx.__name__)
        return df
    except Exception as ex:
        logger.error("Произошла ошибка %s", ex)
        return []
