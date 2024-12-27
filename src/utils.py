import json
import logging
import os
from datetime import datetime
from typing import Any, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_2 = os.getenv("API_KEY_2")


base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_log = os.path.join(base_dir, "..", "logs", "util.log")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=file_path_log,
    encoding="utf-8",
    filemode="w",
)

logger = logging.getLogger()


base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_excel = os.path.join(base_dir, "..", "data", "operations.xlsx")

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_json = os.path.join(base_dir, "..", "user_settings.json")


def get_exel_operations(file=file_path_excel) -> DataFrame:
    """Функция для считывания финансовых операций из Excel-файла"""
    logger.info(f"Запуск функции {get_exel_operations.__name__}")
    if file == "":
        logger.info("Файл пустой")
        excel_data = pd.DataFrame(
            {
                "Дата операции": [],
                "Дата платежа": [],
                "Номер карты": [],
                "Статус": [],
                "Сумма операции": [],
                "Валюта операции": [],
                "Сумма платежа": [],
                "Валюта платежа": [],
                "Кэшбэк": [],
                "Категория": [],
                "МСС": [],
                "Описание": [],
                "Бонусы (включая кэшбэк)": [],
                "Округление на инвесткопилку": [],
                "Сумма операции с округлением": [],
            }
        )
        return excel_data
    try:
        operations = pd.read_excel(file)
        excel_operations = operations.loc[operations["Номер карты"].notnull()]
        logger.info(f"Успешное завершение работы функции {get_exel_operations.__name__}")
        return excel_operations
    except FileNotFoundError as e:
        logger.error(f"Функция {get_exel_operations.__name__} завершилась с ошибкой {e}")
        print(f"Файл {file} не найден.")
        excel_operations = pd.DataFrame()
        return excel_operations
    except Exception as e:
        logger.error(f"Функция {get_exel_operations.__name__} завершилась с ошибкой {e}")
        print(f"Ошибка при чтении файла: {e}")
        excel_operations = pd.DataFrame()
        return excel_operations


def get_data(user_date: Union[str, None]) -> datetime:
    """Функция, преобразующая дату в формат datetime"""
    try:
        logger.info(f"Запуск функции {get_data.__name__}")
        if isinstance(user_date, str):
            logger.info("Преобразуем строку в формат datetime")
            new_date = datetime.strptime(user_date, "%Y-%m-%d %H:%M:%S")
        else:
            logger.info("Значение даты - None, возвращаем текущую дату и время")
            new_date = datetime.now()
        logger.info(f"Успешное завершение работы функции {get_data.__name__}")
        return new_date
    except ValueError as e:
        logger.error(f"Функция {get_data.__name__} завершилась с ошибкой {e}")
        print("Формат даты должен быть 'YYYY-MM-DD HH:MM:SS'.")


def get_data_value(date: Any, df_object: DataFrame) -> DataFrame:
    """Функция, сортирующая значения по дате"""
    end_datetime = get_data(date).replace(hour=23, minute=59, second=59)
    start_datetime = datetime(end_datetime.year, end_datetime.month, 1, 0, 0)
    if "Дата операции" not in df_object.columns:
        logger.error(f"Функция {get_data_value.__name__} завершилась с ошибкой {KeyError}")
        raise KeyError("DataFrame должен содержать колонку 'Дата операции'.")

    try:
        df_object["Дата"] = pd.to_datetime(df_object["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        if df_object["Дата"].isna().any():
            raise ValueError("Некорректный формат в 'Дата операции'.")
        filtered_list = df_object[(df_object["Дата"] >= start_datetime) & (df_object["Дата"] <= end_datetime)]
        logger.info(f"Успешное завершение работы функции {get_data_value.__name__}")
        return filtered_list
    except Exception as e:
        logger.error(f"Функция {get_data_value.__name__} завершилась с ошибкой {e}")
        raise ValueError(f"Ошибка при преобразовании 'Дата операции': {e}")


def get_greeting(date_str: str) -> str:
    """Функция, выводящая приветствие в зависимости от времени суток"""
    logger.info(f"Запуск функции {get_greeting.__name__}")
    time_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    if 6 <= time_obj.hour < 11:
        greeting = "Доброе утро"
    elif 11 <= time_obj.hour < 18:
        greeting = "Добрый день"
    elif 18 <= time_obj.hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    logger.info(f"Успешное завершение работы функции {get_greeting.__name__}")
    return greeting


def get_data_card(df_operations: DataFrame) -> list[dict]:
    """функция, выводящая 4 цифры карты, общую сумму расходов, кешбэк"""
    logger.info(f"Запуск функции {get_data_card.__name__}")

    required_columns = {"Номер карты", "Сумма операции"}
    if not required_columns.issubset(df_operations.columns):
        logger.error(f"Отсутствуют необходимые колонки: {required_columns - set(df_operations.columns)}")
        raise KeyError(f"DataFrame должен содержать колонки: {', '.join(required_columns)}")
    if df_operations.empty:
        logger.warning("Передан пустой DataFrame. Возвращаем пустой список.")
        return []

    card_data = []
    try:
        card_list = df_operations["Номер карты"].unique()  # Уникальные номера карт
        for card in card_list:
            df_data = df_operations.loc[df_operations["Номер карты"] == card]

            total_spent = abs(df_data.loc[df_data["Сумма операции"] < 0, "Сумма операции"].sum())
            round_total = round(total_spent, 2)

            cashback = round(total_spent / 100, 2)
            card_data.append({"last_digits": str(card)[-4:], "total_spent": round_total, "cashback": cashback})
        logger.info(f"Успешное завершение работы функции {get_data_card.__name__}")
    except Exception as e:
        logger.error(f"Функция {get_data_card.__name__} завершилась с ошибкой: {e}")
        raise ValueError(f"Ошибка при обработке данных: {e}")

    return card_data


def get_top_transactions(df_data: DataFrame, top_number=5) -> list[dict]:
    """Топ-5 транзакций по сумме платежа"""
    logger.info(f"Запуск функции {get_top_transactions.__name__}")
    if df_data.empty:
        logger.warning("DataFrame пуст.")
        return []
    df_data["amount"] = df_data["Сумма платежа"].map(float).map(abs)
    sorted_df_data = df_data.sort_values(by="amount", ascending=False, ignore_index=True)
    top_transactions_list = []
    for i in range(min(top_number, len(sorted_df_data))):
        transaction = sorted_df_data.iloc[i]
        date = transaction["Дата платежа"]
        amount = transaction["amount"]
        category = transaction["Категория"]
        description = transaction["Описание"]

        top_transactions_list.append(
            {"date": date, "amount": amount, "category": category, "description": description}
        )

    logger.info(f"Успешное завершение работы функции {get_top_transactions.__name__}")
    return top_transactions_list


def get_currency_rates(date_of_operation: str, file=file_path_json) -> list[dict]:
    """Курс валют"""
    try:
        logger.info(f"Запуск функции {get_currency_rates.__name__}")
        try:
            date_obj = datetime.strptime(date_of_operation, "%Y-%m-%d %H:%M:%S")
            date_string = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            logger.error(f"Некорректный формат даты: {date_of_operation}")
            raise ValueError("Некорректный формат даты. Ожидается 'YYYY-MM-DD HH:MM:SS'.")
        try:
            with open(file, "r", encoding="UTF-8") as f:
                user_currency = json.load(f)
                cur = user_currency.get("user_currencies")
            if not cur or len(cur) < 2:
                raise ValueError("Неверная структура данных в файле. Ожидаются хотя бы 2 валюты.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка при чтении файла: {e}")
            raise FileNotFoundError(f"Не удалось открыть или обработать файл {file}.")
        date = date_string
        url = f"https://api.apilayer.com/exchangerates_data/{date}"
        base_usd = cur[0]
        base_eur = cur[1]
        symbols = "RUB"
        headers = {"apikey": API_KEY}
        payload_1 = {"symbols": symbols, "base": base_usd}
        payload_2 = {"symbols": symbols, "base": base_eur}
        currency_rates = []
        response_usd = requests.get(url, headers=headers, params=payload_1)
        if response_usd.status_code == 200:
            result_usd = response_usd.json()
            currency_rates.append({"currency": base_usd, "rate": round(result_usd["rates"]["RUB"], 2)})
        else:
            logger.warning(f"Не удалось получить курс для {base_usd}. Статус: {response_usd.status_code}")
        response_eur = requests.get(url, headers=headers, params=payload_2)
        if response_eur.status_code == 200:
            result_eur = response_eur.json()
            currency_rates.append({"currency": base_eur, "rate": round(result_eur["rates"]["RUB"], 2)})
        else:
            logger.warning(f"Не удалось получить курс для {base_eur}. Статус: {response_eur.status_code}")
        if currency_rates:
            logger.info(f"Успешное завершение работы функции {get_currency_rates.__name__}")
            return currency_rates
    except requests.exceptions.RequestException as e:
        logger.error(f"Функция {get_currency_rates.__name__} завершилась с ошибкой {e}")
        print("An error occurred. Please try again later.")
    except KeyError:
        logger.error(f"Функция {get_currency_rates.__name__} завершилась с ошибкой {KeyError}")
        print("Некорректный формат транзакции.")


def get_stock_prices(file: str = file_path_json) -> list[dict]:
    """Стоимость акций"""
    try:
        logger.info(f"Запуск функции {get_stock_prices.__name__}")
        with open(file, "r", encoding="UTF-8") as f:
            user_currency = json.load(f)
        stock_prices = []
        for symbol in user_currency.get("user_stocks", []):
            api_url = f"https://api.api-ninjas.com/v1/stockprice?ticker={symbol}"
            response = requests.get(api_url, headers={"X-Api-Key": API_KEY_2})
            if response.status_code == 200:
                logger.info("Статус операции - ОК")
                result_stock = response.json()
                stock_prices.append({"stock": symbol, "rate": result_stock["price"]})
            else:
                logger.warning(f"Ошибка запроса для {symbol}: {response.status_code}")
        return stock_prices
    except FileNotFoundError:
        logger.error(f"Функция {get_stock_prices.__name__} завершилась с ошибкой {FileNotFoundError}")
        print(f"Файл {file} не найден.")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Функция {get_stock_prices.__name__} завершилась с ошибкой {e}")
        print("An error occurred. Please try again later.")
        return []
    except KeyError:
        logger.error(f"Функция {get_stock_prices.__name__} завершилась с ошибкой {KeyError}")
        print("Некорректный формат транзакции.")
        return []


# print(get_stock_prices())
