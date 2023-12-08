import datetime
import os
from unittest.mock import patch

from config import STOCKS_CURRENCIES_PATH
from src.utils import get_converted_date, load_json_file
from src.views import get_currency_rates, get_stock_prices


def test_get_stock_prices() -> None:
    # Параметры для теста
    stocks = ["AAPL", "GOOGL"]
    date_obj = datetime.datetime(2023, 1, 1)

    # Вызов функции
    result = get_stock_prices(stocks, date_obj)

    # Проверки
    assert isinstance(result, list)
    assert len(result) == len(stocks)

    for stock_data in result:
        assert isinstance(stock_data, dict)
        assert len(stock_data) == 1  # Должен быть только один ключ (тикер акции)
        stock_ticker, stock_price = list(stock_data.items())[0]

        assert stock_ticker in stocks
        assert isinstance(stock_price, float)
        assert stock_price >= 0.0  # Цена акции не может быть отрицательной


date_obj = get_converted_date("2021-10-16 16:00:00")
start_date = date_obj.strftime("%Y-%m-%d")
end_date = date_obj.strftime("%Y-%m-%d")

response_request = {
    "success": True,
    "timeseries": True,
    "start_date": "2021-10-16",
    "end_date": "2021-10-16",
    "base": "RUB",
    "rates": {
        "2021-10-16": {
            "AOA": 8.419978,
            "ARS": 1.396743,
            "AUD": 0.018991,
            "AWG": 0.025364,
            "AZN": 0.024004,
            "BIF": 28.132425,
            "BMD": 0.014087,
            "BND": 0.018993,
            "BOB": 0.097358,
            "BRL": 0.076913,
            "BSD": 0.014089,
            "BTC": 2.31408e-07,
            "BTN": 1.056086,
            "BWP": 0.157777,
            "BYN": 0.034612,
            "BYR": 276.111934,
            "BZD": 0.028401,
            "CAD": 0.017436,
            "CDF": 28.329653,
            "CHF": 0.013008,
            "CLF": 0.000421,
            "CLP": 11.604455,
            "CNY": 0.090663,
            "CUP": 0.373315,
            "CVE": 1.344783,
            "CZK": 0.308257,
            "DJF": 2.503608,
            "DKK": 0.090367,
            "DOP": 0.795518,
            "DZD": 1.932939,
            "EGP": 0.221458,
            "ERN": 0.211328,
            "ETB": 0.65718,
            "EUR": 0.012145,
            "FJD": 0.029669,
            "FKP": 0.010329,
            "GBP": 0.010249,
            "GEL": 0.044164,
            "JOD": 0.009988,
            "JPY": 1.611317,
            "KES": 1.562996,
            "KWD": 0.004251,
            "KYD": 0.011741,
            "UGX": 50.864946,
            "USD": 0.014087,
            "UYU": 0.616977,
            "UZS": 150.805018,
            "VEF": 3012299809.101443,
        }
    },
}


@patch("requests.get")
def test_get_currency_rates(mock_get):
    mock_get.return_value.json.return_value = response_request
    assert get_currency_rates(load_json_file(STOCKS_CURRENCIES_PATH)["user_currencies"], date_obj) == [
        {"currency": "USD", "rate": 70.99},
        {"currency": "EUR", "rate": 82.34},
        {"currency": "CHF", "rate": 76.88},
        {"currency": "GBP", "rate": 97.57},
        {"currency": "JPY", "rate": 0.62},
        {"currency": "CAD", "rate": 57.35},
        {"currency": "CNY", "rate": 11.03},
    ]
    mock_get.assert_called_once_with(
        f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base=RUB",
        headers={"apikey": os.getenv("EXCHANGE_RATE_API_KEY")},
        data=[],
    )
