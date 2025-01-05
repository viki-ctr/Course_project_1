import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_log = os.path.join(base_dir, "..", "logs", "reports.log")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=file_path_log,
    encoding="utf-8",
    filemode="w",
)

logger = logging.getLogger()


path_json = "reports.json"


def report(filename=path_json):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4, default=str)
            return result

        return wrapper

    return my_decorator


@report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> list[dict]:
    """Функция траты по категориям"""
    logger.info(f"Запуск функции {spending_by_category.__name__}")
    correct_date = datetime.now()
    try:
        logger.info("Проверяем тип данных при вводе даты")
        if isinstance(date, str):
            correct_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logger.error("Некорректный формат даты")
        print("Дата должна быть в формате 'YYYY-MM-DD'.")

    date_three_month = correct_date - timedelta(days=90)
    logger.info("Проверяем наличие столбцов в документе")
    required_columns = {"Дата операции", "Категория", "Сумма операции"}
    if not required_columns.issubset(transactions.columns):
        logger.error("Отсутствуют нужные столбцы")
        raise ValueError(f"DataFrame должен содержать столбцы: {', '.join(required_columns)}.")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], errors="coerce")
    if transactions["Дата операции"].isnull().any():
        logger.warning("Некоторые даты не удалось преобразовать. Они будут исключены.")
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= date_three_month)
        & (transactions["Дата операции"] <= correct_date)
        & (transactions["Категория"] == category)
    ]

    filtered_transactions = filtered_transactions[filtered_transactions["Сумма операции"] < 0]
    logger.info("Записываем полученный результат")
    result = filtered_transactions.to_dict(orient="records")
    logger.info(f"Функция {spending_by_category.__name__} завершена успешно.")
    return result
