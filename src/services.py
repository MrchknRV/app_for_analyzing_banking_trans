import json

import pandas as pd


# simple_search
def simple_search_by_string(data, search_string):
    try:
        required_data = {"Дата операции", "Номер карты", "Сумма операции", "Категория", "Описание"}
        if not required_data.issubset(data.columns):
            missing = required_data - set(data.columns)
            raise ValueError(f"В файле отсутствуют необходимые колонки: {missing}")
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
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
        return json.dumps(result, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        return json.dumps({"ERROR": "Файл не найден"}, ensure_ascii=False)
    except Exception as ex:
        return json.dumps({"ERROR": f"Произошла ошибка: {str(ex)}"}, ensure_ascii=False)
