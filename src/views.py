import json
import logging
import os

from dotenv import load_dotenv

from config import DATA_PATH_XLSX, PATH
from src.file_reader import reader_file_xlsx
from src.utils import (get_cards_data, get_currency_rates, get_filtered_operations, get_greeting, get_stock_prices,
                       get_top_transactions, load_user_settings)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH / "logs" / "logging.log", "w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] - %(name)r - (%(filename)s).%(funcName)s:%(lineno)-3d - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

load_dotenv()

API_KEY = os.getenv("API_KEY")


def generate_response(input_date, data):
    logger.info("Запуск функции %s со значением %s", generate_response.__name__, input_date)
    settings = load_user_settings()
    df = get_filtered_operations(data, input_date)

    greeting = get_greeting(input_date)
    cards = get_cards_data(df)
    top_transactions = get_top_transactions(df)
    currency_rates = get_currency_rates(settings.get("user_currencies", []))
    stock_prices = get_stock_prices(settings.get("user_stocks", []), api_key=API_KEY)

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return response


if __name__ == "__main__":
    input_date = "2021-12-31 16:44:00"
    data = reader_file_xlsx(DATA_PATH_XLSX)
    response = generate_response(input_date, data)
    print(json.dumps(response, indent=4, ensure_ascii=False))
