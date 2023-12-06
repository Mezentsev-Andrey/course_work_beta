import datetime
import json
import logging
import typing
from pathlib import Path

import pandas as pd

data_path_log = Path(__file__).parent.parent.joinpath("data", "utils.log")
logger = logging.getLogger("__utils__")
file_handler = logging.FileHandler(data_path_log, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def load_xlsx_file(file_path: typing.Any) -> pd.DataFrame:
    """
    Функция загружающая данные из файла Excel в Pandas DataFrame.
    :param file_path: путь к файлу Excel.
    :return: Pandas DataFrame, содержащий данные из файла.
    """
    try:
        # Загрузка данных из файла Excel в Pandas DataFrame
        file_data = pd.read_excel(file_path)
        # Логирование успешного преобразования файла
        logger.info(f"Файл {file_path} успешно преобразован.")
        return file_data
    except FileNotFoundError as error:
        # Логирование ошибки, если файл не найден
        logger.error(f"Файл {file_path} не найден.")
        # Генерация исключения для дальнейшей обработки
        raise error
    except ValueError as error:
        logger.error(f"Произошла ошибка: {str(error)}")
        raise error


def load_json_file(file_path: str) -> dict:
    """
    Функция загружающая данные из файла JSON в объект Python.
    :param file_path: путь к файлу JSON.
    :return: словарь, содержащий данные из файла.
    """
    try:
        # Открываем файл и загружаем данные из JSON
        with open(file_path, "r") as json_file:
            file_data = json.load(json_file)
        # Логирование успешного преобразования файла
        logger.info(f"Файл {file_path} успешно преобразован в объект Python.")
        return file_data
    except FileNotFoundError as error:
        # Логирование ошибки, если файл не найден
        logger.error(f"Файл {file_path} не найден.")
        # Генерация исключения для дальнейшей обработки
        raise error
    except json.JSONDecodeError as error:
        # Логирование ошибки декодирования JSON
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {str(error)}")
        # Генерация исключения для дальнейшей обработки
        raise error


def get_converted_date(date_string: str) -> datetime.datetime:
    """
    Функция преобразующая строку с датой в объект datetime.datetime.
    :param date_string: строка, представляющая дату в формате '%Y-%m-%d %H:%M:%S'.
    :return:объект datetime, представляющий преобразованную дату.
    """
    try:
        # Преобразование строки с датой в объект datetime.datetime
        converted_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        logger.info(f"Дата успешно преобразована: {converted_date}")
        return converted_date
    except ValueError as error:
        logger.error(f"Ошибка преобразования даты: {str(error)}")
        raise error


def filter_operations_by_date(
    operations: pd.DataFrame, date_obj: datetime.datetime
) -> pd.DataFrame:
    """
    Функция фильтрующая успешные операции за месяц, с 1 числа месяца до выбранной даты.
    :param operations: DataFrame с операциями.
    :param date_obj: выбранная дата, до которой происходит фильтрация.
    :return: отфильтрованный DataFrame с успешными операциями за месяц.
    """
    try:
        start_date = date_obj.strftime("%Y.%m.01")
        end_date = date_obj.strftime("%Y.%m.%d")
        operations["Дата операции"] = pd.to_datetime(
            operations["Дата операции"], dayfirst=True
        )

        filtered_operations = operations.loc[
            (operations["Статус"] == "OK")
            & (operations["Дата операции"] >= start_date)
            & (operations["Дата операции"] <= end_date)
        ]

        logger.info("Операции успешно отфильтрованы по дате и статусу 'OK'.")
        return filtered_operations
    except ValueError as error:
        logger.error(f"Ошибка при фильтрации операций: {str(error)}.")
        raise error
    except KeyError as error:
        logger.error(f"Произошла ошибка: {str(error)}.")
        raise error


def get_cards_payments(operations: pd.DataFrame) -> list[dict]:
    """
    Функция выгружающая траты по номеру карты из массива и выдающая их в формате словарей.
    :param operations: DataFrame с операциями.
    :return: список словарей с данными по тратам для каждой карты.
    """
    try:
        cards_list = list(operations["Номер карты"].unique())
        result_list = []

        for card in cards_list:
            card_operations = operations[operations["Номер карты"] == card]
            total_spent = card_operations.loc[
                (card_operations["Сумма операции"] < 0)
                & (card_operations["Валюта операции"] == "RUB"),
                "Сумма операции",
            ].sum()

            card_dict = {
                "last_digits": card[1:],
                "total": round(abs(total_spent), 2),
                "cashback": round(abs(total_spent) * 0.01, 2),
            }

            result_list.append(card_dict)
        logger.info("Данные по картам успешно выданы")
        return result_list
    except ValueError as error:
        logger.error(f"Произошла ошибка: {str(error)}")
        raise error
    except AttributeError as error:
        logger.error(f"Произошла ошибка: {str(error)} из-за несуществующего атрибута")
        raise error


def get_top_five_operations(operations: pd.DataFrame) -> list[dict]:
    """
    Функция возвращающая список словарей с данными по топ-5 операциям для каждой карты.
    :param operations: DataFrame с операциями.
    :return: список словарей с данными по топ-5 операциям для каждой карты.
    """
    try:
        filtered_operations = operations[
            (operations["Сумма операции"] < 0)
            & (operations["Валюта операции"] == "RUB")
        ]
        card_operations = filtered_operations[filtered_operations["Номер карты"] != ""]
        top_five_operations_list = card_operations.nlargest(
            5, "Сумма операции"
        ).to_dict(orient="records")

        result_list = []
        for operation in top_five_operations_list:
            new_dict = {
                "date": pd.to_datetime(operation["Дата операции"]).strftime("%d.%m.%Y"),
                "amount": abs(operation["Сумма операции"]),
                "category": operation.get("Категория"),
                "description": operation.get("Описание"),
            }
            result_list.append(new_dict)

        logger.info("Топ-5 операций успешно получены.")
        return result_list
    except ValueError as error:
        logger.error(f"Ошибка при получении топ-5 операций: {str(error)}")
        raise error
    except AttributeError as error:
        logger.error(f"Произошла ошибка: {str(error)} из-за несуществующего атрибута")
        raise error


def get_greeting_phrase() -> str:
    """
    Функция возвращающая приветственную фразу в зависимости от текущего времени суток.
    :return: приветственная фраза.
    """
    try:
        # Получение текущего времени
        current_time = datetime.datetime.now().time()
        # Определение интервалов времени и соответствующих приветствий
        if current_time < datetime.time(12, 0, 0):
            greeting = "Доброе утро!"
        elif current_time < datetime.time(18, 0, 0):
            greeting = "Добрый день!"
        else:
            greeting = "Добрый вечер!"
        logger.info(f"Приветствие успешно получено: {greeting}")
        return greeting
    except Exception as error:
        logger.error(f"Ошибка при получении приветствия: {str(error)}")
        raise error
