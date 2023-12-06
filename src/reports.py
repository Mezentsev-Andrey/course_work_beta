import typing
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

import pandas as pd


def report_to_file(*, filename: str | typing.Any = "") -> typing.Any:
    """
    Декоратор сохраняющий результат функции в файле.
    :param filename: имя файла для сохранения результата.
    :return: декорированная функция.
    """

    def wrapper(any_func: typing.Callable) -> typing.Callable:
        @wraps(any_func)
        def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            result = any_func(*args, **kwargs)
            if filename:
                saving_place = filename
            else:
                date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                saving_place = Path(
                    Path(__file__).parent.parent.joinpath(
                        "data", "reports", f"{date}_{any_func.__name__}_report.csv"
                    )
                )
                saving_place.parent.mkdir(exist_ok=True, parents=True)
            result.to_csv(saving_place, index=False, encoding="utf-8")

            return result

        return inner

    return wrapper


@report_to_file()
def filter_transactions(
    transactions: pd.DataFrame, category: str, date: str = ""
) -> pd.DataFrame:
    """
    Функция фильтрующая транзакции по указанной категории за определенный временной период.
    :param transactions: DataFrame с данными о транзакциях.
    :param category: категория транзакций, которую нужно отфильтровать.
    :param date: дата в формате "YYYY-MM-DD HH:MM:SS" для определения временного интервала.
    :return: DataFrame с отфильтрованными транзакциями.
    """
    try:
        # Обработка даты
        if date == "":
            date_obj = datetime.now()
        else:
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        # Определение временного интервала (последние 90 дней относительно date_obj)
        start_date = date_obj - timedelta(days=90)
        end_date = date_obj

        # Преобразование формата даты в DataFrame
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], format="%Y-%m-%d %H:%M:%S"
        )

        # Фильтрация данных
        df_by_category = transactions[
            (transactions["Статус"] == "OK")
            & (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Категория"] == category)
        ]

        if report_to_file:
            df_by_category.to_csv(report_to_file, index=False)
        return df_by_category
    except (ValueError, KeyError, TypeError) as error:
        raise error
