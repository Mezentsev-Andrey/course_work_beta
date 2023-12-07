import datetime
import logging
import os
from pathlib import Path

import requests
import yfinance as yf
from dotenv import load_dotenv

data_path_log = Path(__file__).parent.parent.joinpath("data", "views.log")
logger = logging.getLogger("__views__")
file_handler = logging.FileHandler(data_path_log, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def get_stock_prices(stocks: list[str], date_obj: datetime.datetime) -> list[dict]:
    """
     Функция получающая котировки акций для указанных тикеров на заданную дату.
    :param stocks: список тикеров акций.
    :param date_obj: дата для которой нужно получить котировки.
    :return: список словарей, где ключ - тикер акции, значение - цена закрытия на указанную дату.
    """
    try:
        # Преобразование date_obj в строки start_date и end_date
        start_date = date_obj.strftime("%Y-%m-%d")
        end_date = (date_obj + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

        # Список для хранения данных о курсах акций
        stock_list = []

        # Обработка каждой акции в списке
        for stock in stocks:
            stock_data = yf.Ticker(stock)
            data = stock_data.history(start=start_date, end=end_date).head(1)

            if not data.empty:
                one_date_data = data.to_dict(orient="records")[0]
                stock_price = round(one_date_data["Close"], 2)
                stock_list.append({stock: stock_price})
            else:
                logger.warning(f"Нет доступных данных для {stock} на {start_date}")

        # Логирование успешного получения котировок акций
        logger.info("Котировки акций успешно получены.")
        return stock_list
    # Логирование ошибки и выброс исключения дальше
    except Exception as error:
        logger.error(f"Ошибка при получении котировок акций: {str(error)}.")
        raise error


def get_currency_rates(currencies: list, date_obj: datetime.datetime) -> list[dict]:
    """
    Функция выгружающая через APILAYER выбранные курсы валют в выбранную дату
    и выдающая их в форме списка словарей.
    :param currencies: список кодов валют, для которых нужно получить курсы.
    :param date_obj: дата на которую нужно получить курсы валют.
    :return: список словарей с данными о курсах валют.
    """
    load_dotenv()
    # Преобразование дат в формат строки "YYYY-MM-DD"
    start_date_str = date_obj.strftime("%Y-%m-%d")
    end_date_str = date_obj.strftime("%Y-%m-%d")

    # Строительство URL-запроса к API APILAYER
    url = (
        f"https://api.apilayer.com/exchangerates_data/timeseries?"
        f"start_date={start_date_str}&end_date={end_date_str}&base=RUB"
    )
    # Получение ключа API из переменной среды
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    # Создание заголовков запроса с использованием ключа API
    headers = {"apikey": api_key}
    try:
        # Отправка GET-запроса к API APILAYER
        response = requests.get(url, headers=headers, data=[])
        # Проверка успешности запроса
        response.raise_for_status()
        # Преобразование ответа от API в словарь Python
        currency_dict = response.json()
        # Создание пустого списка для хранения данных о курсах валют
        currency_list = []

        # Итерация по списку валют
        for currency in currencies:
            # Создание пустого словаря для хранения данных о курсе текущей валюты
            dict_currency = {}
            # Запись названия текущей валюты в словарь
            dict_currency["currency"] = currency
            # Вычисление обратного значения курса валюты относительно базовой (RUB)
            dict_currency["rate"] = round(
                1 / float(currency_dict["rates"][start_date_str][currency]), 2
            )
            # Добавление словаря в общий список
            currency_list.append(dict_currency)

        # Логирование успешного получения курсов валют
        logger.info("Курсы валют успешно получены.")
        # Возвращение списка словарей с информацией о курсах валют
        return currency_list
    except Exception as error:
        # Логирование ошибки и выброс исключения дальше
        logger.error(f"Ошибка при получении курсов валют: {error}")
        raise error
