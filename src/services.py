import logging
from datetime import datetime
from pathlib import Path
from typing import Any

data_path_log = Path(__file__).parent.parent.joinpath("data", "services.log")
logger = logging.getLogger("__services__")
file_handler = logging.FileHandler(data_path_log, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def investment_income(month: str, transactions: list[dict], limit: int) -> int:
    """
    Функция рассчитывающая доход от инвестиций за указанный месяц.
    :param month: строка с указанием месяца в формате "YYYY-MM".
    :param transactions: список словарей с данными о транзакциях.
    :param limit: лимит для округления суммы транзакций в копилке.
    :return: cумма денег в копилке после округления транзакций
    """
    try:
        # Преобразование месяца
        datetime_month = datetime.strptime(month, "%Y-%m")
        corr_month = datetime_month.strftime("%m.%Y")

        # Выборка транзакций
        required_transactions = [
            t
            for t in transactions
            if t.get("Статус") == "OK"
            and datetime.strptime(t.get("Дата операции"), "%Y-%m-%d").strftime("%m.%Y")
            == corr_month
        ]

        # Расчет суммы в копилке
        money_in_kopilka = 0
        for transaction in required_transactions:
            amount = transaction.get("Сумма платежа")
            abs_amount = abs(amount)

            if amount < 0 and abs_amount % limit != 0:
                if limit == 50:
                    round_amount = limit * ((abs_amount // limit) + 1) - abs_amount
                elif limit in [10, 100]:
                    round_amount = limit * ((abs_amount // limit) + 1) - abs_amount
                else:
                    round_amount = 0
                money_in_kopilka += round_amount
        logger.info("Копилка успешно наполнена")
        # Возврат результата
        return money_in_kopilka

    except (ValueError, KeyError, TypeError) as error:
        # Логирование ошибки и повторное вызов исключения
        print(f"Ошибка обработки транзакций: {str(error)}")
        raise error
