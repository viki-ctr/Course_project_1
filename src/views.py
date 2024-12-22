import os
from typing import Union, Any
from datetime import datetime as dt, timedelta
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
                parsed_date = dt.strptime(current_date, "%d.%m.%Y %H:%M:%S")

            except ValueError:
                parsed_date = parser.parse(current_date)
                return parsed_date.strftime("%d.%m.%Y %H:%M:%S")

        elif isinstance(current_date, list):
            parsed_date = parser.parse("-".join(current_date))

        else:
            return "Неверный формат данных"

        end_datetime = parsed_date
        start_datetime = dt(end_datetime.year, end_datetime.month, 1, 0,0)
        datetime_range = []
        date_for_range = start_datetime
        while date_for_range <= end_datetime:
            datetime_range.append(date_for_range.strftime("%d.%m.%Y %H:%M:%S"))
            date_for_range += timedelta(seconds=1)
        return datetime_range

    except Exception as e:
        return f"Ошибка при обработке даты: {e}"


print(get_data("2019.07.17 15:05:27"))
