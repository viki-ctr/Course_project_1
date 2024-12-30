import logging
import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List
from dateutil.parser import parse

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_log = os.path.join(base_dir, "..", "logs", "services.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=file_path_log,
    encoding="utf-8",
    filemode="w",
)

logger = logging.getLogger()


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """Инвесткопилка. Позволяет копить через округление трат"""
    logger.info(f"Запуск функции {investment_bank.__name__}")
    try:
        month_date = datetime.strptime(month, "%Y-%m")
        logger.info("Корректный ввод даты")

    except ValueError:
        logger.error("Ошибка. Некорреткный формат даты")
        raise ValueError("Некорректный формат даты. Ожидается 'YYYY-MM'.")

    total_savings = 0.0

    for transaction in transactions:
        if "Дата операции" not in transaction or "Сумма операции" not in transaction:
            logger.warning("Проверяем наличие ключей в словаре")
            continue
        try:
            logger.info("проверяем относится ли транзакция к указанному месяцу")
            # transaction_date = datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            transaction_date = parse(transaction["Дата операции"], dayfirst=False)
            start_of_month = month_date.replace(day=1)
            end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            # if transaction_date.year == month_date.year and transaction_date.month == month_date.month:
            if start_of_month <= transaction_date <= end_of_month:
                amount = transaction["Сумма операции"]
                logger.info("Округляем разницу и добавляем в копилку")
                # rounded_amount = (amount // limit + 1) * limit if amount > 0 else (amount // limit) * limit
                rounded_amount = (amount + limit - 1) // limit * limit
                savings = max(0, rounded_amount - amount)
                total_savings += savings
                logger.info(f"Общее накопление после транзакции: {total_savings}")
            else:
                logger.info(f"Транзакция не относится к месяцу {month}")
        except (ValueError, TypeError):
            logger.error("Транзакция некорректна")
            continue
    total_round = round(total_savings, 2)
    investment_piggy_bank = json.dumps({"Отложенная сумма": total_round}, ensure_ascii=False)
    logger.info(f"Функция {investment_bank.__name__} завершена успешно.")
    return investment_piggy_bank


transactions = [
        {"Дата операции": "2023-12-01", "Сумма операции": 120.0},
        {"Дата операции": "2023-12-15", "Сумма операции": 45.0},
        {"Дата операции": "2023-11-20", "Сумма операции": 200.0},
        {"Дата операции": "31.12.2023 16:44:00", "Сумма операции": 30.0}
    ]
result = investment_bank("2023-12", transactions, 50)
print(result)