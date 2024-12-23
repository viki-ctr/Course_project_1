import os
from typing import Any
from datetime import datetime, timedelta
from dateutil import parser


import pandas as pd
from pandas import DataFrame
from collections import Counter


def file_path():
    """Функция, принимающая путь до файла"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_excel = os.path.join(base_dir, "..", "data", "operations.xlsx")
    return file_path_excel


def get_exel_operations(file=None) -> DataFrame:
    """Функция для считывания финансовых операций из Excel-файла"""
    if file == "":
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
        file = file_path()
        operations = pd.read_excel(file)
        excel_operations = operations.loc[operations["Номер карты"].notnull()]
        return excel_operations
    except FileNotFoundError:
        print(f"Файл {file} не найден.")
        excel_operations = pd.DataFrame()
        return excel_operations
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        excel_operations = pd.DataFrame()
        return excel_operations


# print(get_exel_operations())


def get_data(current_date: Any, df: DataFrame) -> DataFrame:
    """Функция, преобразующая дату в формат datetime"""

    if isinstance(current_date, str):
        try:
            current_date_new = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Формат current_date должен быть 'YYYY-MM-DD HH:MM:SS'.")
    elif current_date is None:
        current_date_new = datetime.now()

    end_datetime = current_date_new
    start_datetime = datetime(end_datetime.year, end_datetime.month, 1, 0, 0)
    if "Дата операции" not in df.columns:
        raise KeyError("DataFrame должен содержать колонку 'Дата операции'.")

    try:
        df["Дата"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        filtered_df = df[(df["Дата"] >= start_datetime) & (df["Дата"] <= end_datetime)]
        return filtered_df
    except Exception as e:
        raise ValueError(f"Ошибка при преобразовании 'Дата операции': {e}")


# df = get_exel_operations()
# current_date = "2019-12-20 23:59:59"
# filtered_df = get_data(current_date, df)
# print(filtered_df)


def get_greeting(date_str: str) -> str:
    """Функция, выводящая приветствие в зависимости от времени суток"""
    time_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
    if 6 <= time_obj.hour < 11:
        greeting = "Доброе утро"
    elif 11 <= time_obj.hour < 18:
        greeting = "Добрый день"
    elif 18 <= time_obj.hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    return greeting


# print(get_greeting("17.07.2019 00:05:27"))


def get_data_card(df_operations: DataFrame) -> list[dict]:
    """функция, выводящая 4 цифры карты, общую сумму расходов, кешбэк """
    df_operations = get_exel_operations(df_operations)
    card_list = df_operations["Номер карты"].unique()
    card_data = []
    for card in card_list:
        df_data = df_operations.loc[df_operations.loc[:, "Номер карты"] == card]
        total_spent = float(abs(df_data[df_data["Сумма операции"] < 0]["Сумма операции"].sum()))
        round_total = round(total_spent, 2)
        cashback = round(total_spent / 100, 2)
        card_data.append({"last_digits": str(card)[-4:],
                          "total_spent": round_total,
                          "cashback": cashback})
    return card_data


# print(get_data_card(get_exel_operations))


def get_top_transactions(df_data: DataFrame, top_number=5) -> list[dict]:
    """Топ-5 транзакций по сумме платежа"""

    top_transactions_list = []
    df = df_data.loc[::]
    df["amount"] = df.loc[:, "Сумма платежа"].map(float).map(abs)
    sorted_df_data = df.sort_values(by="amount", ascending=False, ignore_index=True)
    for i in range(top_number):
        date = sorted_df_data.loc[i, "Дата платежа"]
        amount = float(sorted_df_data.loc[i, "amount"])
        category = sorted_df_data.loc[i, "Категория"]
        description = sorted_df_data.loc[i, "Описание"]
        top_transactions_list.append(
            {"date": date, "amount": amount, "category": category, "description": description}
        )
    return top_transactions_list

df = get_exel_operations()
print(get_top_transactions(df))