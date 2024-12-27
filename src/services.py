import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, List

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_log = os.path.join(base_dir, "..", "logs", "services.log")

logging.basicConfig(
    level=logging.WARNING,
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
            logger.info("Проверяем наличие ключей в словаре")
            continue
        try:
            logger.info("проверяем относится ли транзакция к указанному месяцу")
            transaction_date = datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            if transaction_date.year == month_date.year and transaction_date.month == month_date.month:
                amount = transaction["Сумма операции"]
                logger.info("Округляем разницу и добавляем в копилку")
                rounded_amount = (amount // limit + 1) * limit if amount > 0 else (amount // limit) * limit
                savings = max(0, rounded_amount - amount)
                total_savings += savings
                total_round = round(total_savings, 2)
                investment_piggy_bank = json.dumps({ "Отложенная сумма": total_round}, ensure_ascii=False)
        except (ValueError, TypeError):
            logger.error("Транзакция некорректна")
            continue
    logger.info(f"Функция {investment_bank.__name__} завершена успешно.")
    return investment_piggy_bank

#
# transactions = [
#     {"Дата операции": "2024-12-10", "Сумма операции": 245.34},
#     {"Дата операции": "2024-12-15", "Сумма операции": 50.99},
#     {"Дата операции": "2024-12-20", "Сумма операции": 395.78},
#     {"Дата операции": "2024-11-30", "Сумма операции": 120.56},
#     {"Дата операции": "2024-12-05", "Сумма операции": 151.90}
# ]
# savings = investment_bank("2024-12", transactions, 50)
# # print(f"Отложенная сумма: {savings} ₽")
# print(savings)