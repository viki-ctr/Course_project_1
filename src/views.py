import json
import logging
import os

from src.utils import (
    get_currency_rates,
    get_data_card,
    get_data_value,
    get_exel_operations,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
)

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_log = os.path.join(base_dir, "..", "logs", "views.log")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=file_path_log,
    encoding="utf-8",
    filemode="w",
)

logger = logging.getLogger()


def main_page(date: str):
    """Функция, принимающая информацию о главной странице"""
    logger.info(f"Запуск функции {main_page.__name__}")
    try:
        df = get_exel_operations()
        if df is None or df.empty:
            logger.error("Ошибка: Не удалось загрузить данные из Excel.")
            return json.dumps({"error": "Не удалось загрузить данные из Excel."})

        filtered = get_data_value(date, df)
        greeting = get_greeting(date)
        cards_info = get_data_card(filtered)
        top_transactions = get_top_transactions(filtered)
        currency_rates = get_currency_rates(date)
        stock_rates = get_stock_prices()
        main_page_info = json.dumps(
            {
                "greeting": greeting,
                "cards": cards_info,
                "top_transactions": top_transactions,
                "currency_rates": currency_rates,
                "stock_prices": stock_rates,
            },
            ensure_ascii=False,
        )
        logger.info(f"Функция {main_page.__name__} завершена успешно.")
        return main_page_info
    except Exception as e:
        logger.error(f"Ошибка при выполнении функции {main_page.__name__}: {e}")
        return json.dumps({"error": f"Произошла ошибка: {str(e)}"})


# print(main_page("2021-12-21 14:30:00"))
