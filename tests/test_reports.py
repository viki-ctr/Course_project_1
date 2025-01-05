import tempfile
import pytest

import pandas as pd

from src.reports import report, spending_by_category


def test_report(capsys):
    """Тестирует запись в файл после успешного выполнения"""

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        log_file_path = tmp_file.name

    @report(filename=log_file_path)
    def func(x, y):
        return x + y

    func(1, 2)

    with open(log_file_path, "r", encoding="utf-8") as file:
        logs = file.read()

    assert "3" in logs


def test_spending_by_category_valid_data():
    """Тест на корректную обработку данных."""
    df = pd.DataFrame({
        "Дата операции": ["2023-12-01", "2023-12-10", "2023-11-05"],
        "Категория": ["Еда", "Еда", "Транспорт"],
        "Сумма операции": [-1000, -500, -200]
    })
    result = spending_by_category(df, category="Еда", date="2023-12-10")

    assert len(result) == 2
    assert all(record['Категория'] == "Еда" for record in result)
    assert all(record['Сумма операции'] < 0 for record in result)


def test_spending_by_category_missing_columns():
    df = pd.DataFrame({
        "Дата операции": ["2023-12-01", "2023-12-10", "2023-11-05"],
        "Категория": ["Еда", "Еда", "Транспорт"]
    })

    with pytest.raises(ValueError):
        spending_by_category(df, category="Еда", date="2023-12-10")


def test_spending_by_category_none_date():
    """Тест на обработку None как даты."""
    df = pd.DataFrame({
        "Дата операции": ["2023-12-01", "2023-12-10", "2023-11-05"],
        "Категория": ["Еда", "Еда", "Транспорт"],
        "Сумма операции": [-1000, -500, -200]
    })

    # Тестируем с None в параметре даты
    result = spending_by_category(df, category="Еда", date=None)
    assert len(result) == 0
