from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import json
import unittest
import requests
import os

import pandas as pd
import pytest

from src.utils import (get_currency_rates, get_data, get_data_card, get_data_value, get_exel_operations, get_greeting,
                       get_stock_prices, get_top_transactions)
from tests.conftest import empty_df, transactions_df_test


@patch("src.utils.pd.read_excel")
def test_get_exel_operations(mock_read_excel, empty_df):
    mock_read_excel.return_value = empty_df
    assert get_exel_operations("test.xlsx").equals(empty_df)
    mock_read_excel.assert_called_once_with("test.xlsx")


def test_get_data():
    input_date = "2023-12-21 15:30:00"
    expected_date = datetime(2023, 12, 21, 15, 30, 0)
    result = get_data(input_date)
    assert result == expected_date


@patch("src.utils.datetime")
def test_none_date(mock_datetime):
    mock_now = datetime(2023, 12, 21, 15, 30, 0)
    mock_datetime.now.return_value = mock_now
    result = get_data(None)
    assert result == mock_now


def test_invalid_date_string(caplog):
    input_date = "21-12-2023 15:30:00"
    with caplog.at_level("ERROR"):
        result = get_data(input_date)
        assert result is None, "Функция должна возвращать None при ValueError."


def test_missing_date_column():
    df = pd.DataFrame({"Категория": ["Продукты"], "Сумма операции": [-1000]})
    with pytest.raises(KeyError, match="DataFrame должен содержать колонку 'Дата операции'."):
        get_data_value("2023-12-01 10:00:00", df)


def test_invalid_date_format():
    df = pd.DataFrame({
        "Дата операции": ["32.12.2023 10:00:00", "15.11.2023 12:00:00"],
        "Сумма операции": [-1000, -500]
    })
    with pytest.raises(ValueError, match="Ошибка при преобразовании 'Дата операции': .*"):
        get_data_value("2023-12-01 10:00:00", df)


def test_valid_data():
    df = pd.DataFrame({
        "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 12:00:00", "30.11.2023 08:00:00"],
        "Сумма операции": [1000, 500, 200]
    })
    result = get_data_value("2023-12-15 10:00:00", df)
    assert len(result) == 2
    expected_dates = pd.to_datetime(["01.12.2023 10:00:00", "15.12.2023 12:00:00"], format="%d.%m.%Y %H:%M:%S")
    assert set(result["Дата"]) == set(expected_dates)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Дата операции", "Сумма операции"])
    result = get_data_value("2023-12-15 10:00:00", df)
    assert result.empty


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ("2023-01-01 06:05:04", "Доброе утро"),
        ("2023-01-22 13:05:04", "Добрый день"),
        ("2023-01-01 20:05:04", "Добрый вечер"),
        ("2023-01-22 01:05:04", "Доброй ночи"),
    ],
)
def test_get_greeting(input_data, expected):
    assert get_greeting(input_data) == expected


def test_get_data_card(transactions_df_test):
    test_data = transactions_df_test
    expected_result = [
        {"last_digits": "3456", "total_spent": 301.25, "cashback": 3.01},
        {"last_digits": "7654", "total_spent": 50.25, "cashback": 0.5}
    ]
    result = get_data_card(test_data)
    assert len(result) == len(expected_result), "Неверное количество карт в результате"
    for expected, actual in zip(expected_result, result):
        assert expected == actual, f"Ожидалось {expected}, но получено {actual}"


def test_missing_columns():
    df = pd.DataFrame({
        "Invalid Column": ["1234567890123456"],
        "Amount": [-150.0]
    })
    with pytest.raises(KeyError, match="DataFrame должен содержать колонки: Сумма операции, Номер карты"):
        get_data_card(df)


def test_empty_dt_frame():
    df = pd.DataFrame(columns=["Номер карты", "Сумма операции"])
    result = get_data_card(df)
    assert result == []


def test_no_negative_transactions():
    data = {
        "Номер карты": ["1234567890123456"],
        "Сумма операции": [100.0]
    }
    df = pd.DataFrame(data)
    result = get_data_card(df)
    expected = [
        {"last_digits": "3456", "total_spent": 0.0, "cashback": 0.0}
    ]
    assert result == expected


def test_incorrect_data_format():
    data = {
        "Номер карты": ["1234567890123456"],
        "Сумма операции": ["NotNumber"]
    }
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Ошибка при обработке данных"):
        get_data_card(df)


def test_multiple_cards():
    data = {
        "Номер карты": ["1234567890123456", "9876543210987654", "1234567890123456"],
        "Сумма операции": [-100.0, -200.0, -50.0]
    }
    df = pd.DataFrame(data)
    result = get_data_card(df)
    expected = [
        {"last_digits": "3456", "total_spent": 150.0, "cashback": 1.5},
        {"last_digits": "7654", "total_spent": 200.0, "cashback": 2.0}
    ]
    assert result == expected


def test_get_top_transactions(sample_data):
    result = get_top_transactions(sample_data, top_number=2)

    assert len(result) == 2
    assert result[0]["amount"] > result[1]["amount"]
    assert result[0]["category"] == "Одежда"
    assert result[1]["category"] == "Транспорт"


def test_get_top_transactions_empty_data():
    empty_df = pd.DataFrame(columns=["Дата платежа", "Сумма платежа", "Категория", "Описание"])
    result = get_top_transactions(empty_df)
    assert result == []


def test_get_top_transactions_single_row():
    single_row_df = pd.DataFrame({
        "Дата платежа": ["2023-12-01"],
        "Сумма платежа": [1000],
        "Категория": ["Еда"],
        "Описание": ["Покупка еды"]
    })
    result = get_top_transactions(single_row_df, top_number=5)
    assert len(result) == 1


def test_get_top_transactions_format():
    data = {
        "Дата платежа": ["2023-12-01", "2023-12-02", "2023-12-03"],
        "Сумма платежа": [100, 500, 200],
        "Категория": ["Продукты", "Транспорт", "Шоппинг"],
        "Описание": ["Покупка еды", "Бензин", "Одежда"]
    }
    df = pd.DataFrame(data)

    result = get_top_transactions(df, 3)

    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert 'date' in result[0]
    assert 'amount' in result[0]


def test_get_currency_rates_success():
    with patch("builtins.open", mock_open(read_data=json.dumps({
        "user_currencies": ["USD", "EUR"]
    }))), patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"RUB": 75.0}}
        date_of_operation = "2023-12-01 14:00:00"
        result = get_currency_rates(date_of_operation)
        expected_result = [
            {"currency": "USD", "rate": 75.0},
            {"currency": "EUR", "rate": 75.0}
        ]
        assert result == expected_result, f"Expected {expected_result}, but got {result}"


mock_file_data = json.dumps({"user_stocks": ["AAPL", "GOOGL"]})

mock_valid_api_response = {"price": 150.25}
mock_invalid_api_response = {"error": "Invalid API key"}


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open)
def test_get_stock_prices_file_not_found(mock_file, mock_requests_get):
    mock_file.side_effect = FileNotFoundError
    result = get_stock_prices(file="non_existent_file.json")
    assert result == [], "Expected an empty list when the file is not found"
    mock_file.assert_called_once_with("non_existent_file.json", "r", encoding="UTF-8")


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data=mock_file_data)
def test_get_stock_prices_api_error(mock_file, mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 401  # Unauthorized
    mock_requests_get.return_value = mock_response
    result = get_stock_prices(file="mock_file_path.json")
    expected_result = []
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"user_stocks": []}))
def test_get_stock_prices_empty_stocks(mock_file, mock_requests_get):
    result = get_stock_prices(file="mock_file_path.json")

    assert result == [], "Expected an empty list when user_stocks is empty"
    mock_file.assert_called_once_with("mock_file_path.json", "r", encoding="UTF-8")


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data=mock_file_data)
def test_get_stock_prices_invalid_api_response(mock_file, mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_invalid_api_response  # Invalid response
    mock_requests_get.return_value = mock_response

    result = get_stock_prices(file="mock_file_path.json")
    expected_result = []
    assert result == expected_result, f"Expected {expected_result}, but got {result}"