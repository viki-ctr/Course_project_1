import os
from typing import Union, Any
from datetime import datetime, timedelta

from dateutil import parser

import pandas as pd


def file_path():
    """Функция, принимающая путь до файла"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_excel = os.path.join(base_dir, "..", "data", "operations.xlsx")
    return file_path_excel


def get_exel_operations(file=None):
    """Функция для считывания финансовых операций из Excel-файла"""
    if file is None:
        file = file_path()
    try:
        operations = pd.read_excel(file)
        return operations.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Файл {file} не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


# print(get_exel_operations())


def get_data(current_date: Union[str, list]) -> Any:
    """Функция, преобразующая дату в формат datetime"""
    try:
        if isinstance(current_date, str):
            try:
                parsed_date = datetime.strptime(current_date, "%Y.%m.%d %H:%M:%S")

            except ValueError:
                parsed_date = parser.parse(current_date)
                return parsed_date.strftime("%d.%m.%Y %H:%M:%S")

        elif isinstance(current_date, list):
            parsed_date = parser.parse("-".join(current_date))

        else:
            return "Неверный формат данных"
        end_datetime = parsed_date
        start_datetime = datetime(end_datetime.year, end_datetime.month, 1, 0, 0)
        datetime_range = []
        date_for_range = start_datetime
        while date_for_range <= end_datetime:
            datetime_range.append(date_for_range.strftime("%d.%m.%Y %H:%M:%S"))
            date_for_range += timedelta(seconds=1)
        return datetime_range

    except Exception as e:
        return f"Ошибка при обработке даты: {e}"


# print(get_data("2019.07.02 03:05:27"))


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


