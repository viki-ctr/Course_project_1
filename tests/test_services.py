from src.services import investment_bank
import pytest


def test_investment_bank_valid_data():
    transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": 120.0},
        {"Дата операции": "2023-12-15", "Сумма операции": 45.0},
        {"Дата операции": "2023-11-20", "Сумма операции": 200.0}
    ]
    result = investment_bank("2023-12", transactions, 50)
    assert result == '{"Отложенная сумма": 35.0}'


def test_investment_bank_invalid_date():
    transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": -120},
        {"Дата операции": "2023-12-15", "Сумма операции": -45}
    ]

    with pytest.raises(ValueError):
        investment_bank("2023-13", transactions, 50)


def test_investment_bank_missing_keys():
    transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": -120},
        {"Дата операции": "2023-12-15"}  # Отсутствует 'Сумма операции'
    ]
    result = investment_bank("2023-12", transactions, 50)
    assert result == '{"Отложенная сумма": 0.0}'


def test_investment_bank_positive_negative_transactions():
    transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": -120},
        {"Дата операции": "2023-12-15", "Сумма операции": 60},  # Положительная сумма
        {"Дата операции": "2023-12-20", "Сумма операции": -45}
    ]
    result = investment_bank("2023-12", transactions, 50)
    assert result == '{"Отложенная сумма": 40.0}'


def test_investment_bank_invalid_transaction_data():
    transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": "abc"},  # Некорректная сумма
        {"Дата операции": "2023-12-15", "Сумма операции": -50}
    ]
    result = investment_bank("2023-12", transactions, 50)
    assert result == '{"Отложенная сумма": 0.0}'
