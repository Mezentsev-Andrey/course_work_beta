from pprint import pprint

from config import OPERATIONS_PATH, STOCKS_CURRENCIES_PATH
from src.utils import (filter_operations_by_date, get_cards_payments,
                       get_converted_date, get_greeting_phrase,
                       get_top_five_operations, load_json_file, load_xlsx_file)
from src.views import get_currency_rates, get_stock_prices

if __name__ == "__main__":
    input_date = "2021-12-13 16:00:00"

    user_stocks = load_json_file(STOCKS_CURRENCIES_PATH)["user_stocks"]
    user_currencies = load_json_file(STOCKS_CURRENCIES_PATH)["user_currencies"]

    def main(date: str) -> dict[str]:
        """
        Функция принимающая на вход строку с датой и возвращающая JSON-ответ с данными для главной страницы.
        :param date: строка с датой в формате "YYYY-MM-DD".
        :return: словарь с данными для главной страницы.
        """
        try:
            date_obj = get_converted_date(date)
            operations = load_xlsx_file(OPERATIONS_PATH)
            filtered_operations = filter_operations_by_date(operations, date_obj)

            response_dict = {
                "greeting": get_greeting_phrase(),
                "cards": get_cards_payments(filtered_operations),
                "top_transactions": get_top_five_operations(filtered_operations),
                "currency_rates": get_currency_rates(user_currencies, date_obj),
                "stock_prices": get_stock_prices(user_stocks, date_obj),
            }
            return response_dict
        except Exception as error:
            print(f"Произошла ошибка: {str(error)}")
            return {"error": "Произошла непредвиденная ошибка"}

    pprint(main(input_date))
