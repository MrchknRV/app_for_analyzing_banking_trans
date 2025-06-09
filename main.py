from config import DATA_PATH_XLSX
from src.file_reader import reader_file_xlsx
from src.reports import spending_by_category
from src.services import simple_search_by_string
from src.views import generate_response

if __name__ == "__main__":
    data = reader_file_xlsx(DATA_PATH_XLSX)
    input_date = "2021-12-31 12:12:12"
    search_word = "Фастфуд"
    category = "Переводы"
    result_response = generate_response(input_date, data)
    result_search = simple_search_by_string(data, search_word)
    result_spending = spending_by_category(data, category, input_date)

    print(result_response)
    print("-" * 10)
    print(result_search)
    print("-" * 10)
    print(result_spending)
