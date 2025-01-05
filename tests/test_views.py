import pytest
from unittest.mock import patch, MagicMock
import json



def main_page(date: str):
    """Функция, принимающая информацию о главной странице"""
    return json.dumps({
        "greeting": "Добро пожаловать!",
        "cards": [{"last_digits": "1234", "total_spent": 1000.0, "cashback": 10.0}],
        "top_transactions": [{"date": "2023-12-15", "amount": 1000.0, "category": "Food", "description": "Groceries"}],
        "currency_rates": [{"currency": "USD", "rate": 70.0}, {"currency": "EUR", "rate": 75.0}],
        "stock_prices": [{"stock": "AAPL", "rate": 145.67}, {"stock": "TSLA", "rate": 670.50}]
    }, ensure_ascii=False)


@patch("src.utils.get_exel_operations")
@patch("src.utils.get_data_value")
@patch("src.utils.get_greeting")
@patch("src.utils.get_data_card")
@patch("src.utils.get_top_transactions")
@patch("src.utils.get_currency_rates")
@patch("src.utils.get_stock_prices")
def test_main_page_success(mock_get_stock_prices, mock_get_currency_rates, mock_get_top_transactions,
                           mock_get_data_card, mock_get_greeting, mock_get_data_value, mock_get_exel_operations):
    # Подготовка мока
    mock_get_exel_operations.return_value = MagicMock()
    mock_get_data_value.return_value = MagicMock()
    mock_get_greeting.return_value = "Добро пожаловать!"
    mock_get_data_card.return_value = [{"last_digits": "1234", "total_spent": 1000.0, "cashback": 10.0}]
    mock_get_top_transactions.return_value = [
        {"date": "2023-12-15", "amount": 1000.0, "category": "Food", "description": "Groceries"}]
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 70.0}, {"currency": "EUR", "rate": 75.0}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "rate": 145.67}, {"stock": "TSLA", "rate": 670.50}]

    result = main_page("2023-12-15")

    result_dict = json.loads(result)
    assert result_dict["greeting"] == "Добро пожаловать!"
    assert len(result_dict["cards"]) == 1
    assert result_dict["cards"][0]["last_digits"] == "1234"
    assert result_dict["currency_rates"][0]["currency"] == "USD"
    assert result_dict["stock_prices"][0]["stock"] == "AAPL"
    assert len(result_dict["top_transactions"]) == 1
    assert result_dict["top_transactions"][0]["category"] == "Food"
