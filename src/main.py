from src.reports import spending_by_category
from src.services import investment_bank
from src.views import main_page


def main() -> None:
    """Функция, реализующая функционал всех функций"""
    user_date = input("Введите дату ")
    main_user_page = main_page(user_date)
    user_services = input("Введите месяц, выберите файл операций, предел, до которого округляются суммы")
    user_investment_bank = investment_bank(user_services)
    user_reports = input("Выберите файл транзакций, выберите категорию и дату")
    user_spending_by_category = spending_by_category(user_reports)
    print(f"Главная: {main_user_page}")
    print(f"Сервисы: {user_investment_bank}")
    print(f"Отчеты: {user_spending_by_category}")


if __name__ == "__main__":
    main()
