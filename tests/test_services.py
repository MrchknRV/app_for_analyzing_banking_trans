import json

import pandas as pd

from src.services import simple_search_by_string


def test_successful_search(sample_data_service) -> None:
    search_string = "Ресторан"
    result = simple_search_by_string(sample_data_service, search_string)
    result_data = json.loads(result)

    assert result_data["count"] == 1
    assert len(result_data["operations"]) == 1
    assert result_data == {
        "count": 1,
        "operations": [
            {
                "date": "02.01.2023",
                "cards": "5678",
                "amount": 200.75,
                "category": "Ресторан",
                "description": "Ужин в ресторане",
            }
        ],
    }


def test_case_search(sample_data_service) -> None:
    search_string = "АШАН"
    result = simple_search_by_string(sample_data_service, search_string)
    result_data = json.loads(result)

    assert result_data["count"] == 1
    assert result_data["operations"][0]["description"] == "Покупка в Ашане"


def test_multi_matches(sample_data) -> None:
    search_string = "Фастфуд"
    result = simple_search_by_string(sample_data, search_string)
    result_data = json.loads(result)

    assert result_data["count"] == 2
    assert result_data == {
        "count": 2,
        "operations": [
            {
                "date": "30.12.2021",
                "cards": "5091",
                "amount": -1411.4,
                "category": "Фастфуд",
                "description": "Пополнение через Газпромбанк",
            },
            {"date": "29.12.2021", "cards": "4556", "amount": -35.0, "category": "Фастфуд", "description": "РЖД"},
        ],
    }


def test_missing_column() -> None:
    invalid_data = pd.DataFrame({"Дата": ["01.01.2023"], "Сумма": [100.0]})

    result = simple_search_by_string(invalid_data, "test")
    result_data = json.loads(result)

    assert "ERROR" in result_data
    assert "отсутствуют необходимые колонки" in result_data["ERROR"]


def test_empty_result(sample_data) -> None:
    result = simple_search_by_string(sample_data, "несуществующий запрос")
    result_data = json.loads(result)

    assert result_data["count"] == 0
    assert len(result_data["operations"]) == 0


def test_null_card_number(sample_data_service) -> None:
    result = simple_search_by_string(sample_data_service, "такси")
    result_data = json.loads(result)

    assert result_data["operations"][0]["cards"] == "Нет данных"


def test_json_structure(sample_data_service) -> None:
    result = simple_search_by_string(sample_data_service, "ресторан")
    result_data = json.loads(result)

    assert set(result_data.keys()) == {"count", "operations"}
    assert isinstance(result_data["count"], int)
    assert isinstance(result_data["operations"], list)

    if result_data["operations"]:
        operation = result_data["operations"][0]
        assert set(operation.keys()) == {"date", "cards", "amount", "category", "description"}
