import pytest

from src.services import investment_income


def test_investment_income_valid_input():
    # Проверка успешного расчета дохода от инвестиций
    month = "2023-01"
    transactions = [
        {"Статус": "OK", "Дата операции": "2023-01-15", "Сумма платежа": -75},
        {"Статус": "OK", "Дата операции": "2023-01-20", "Сумма платежа": 50},
        {"Статус": "OK", "Дата операции": "2023-02-01", "Сумма платежа": -30},
    ]
    limit = 50

    result = investment_income(month, transactions, limit)
    assert result == 25


def test_investment_income_empty_transactions():
    # Проверка возврата 0 при отсутствии транзакций
    month = "2023-12"
    transactions = []
    limit = 50

    result = investment_income(month, transactions, limit)
    assert result == 0


def test_investment_income_invalid_input():
    # Проверка обработки ошибки при некорректных входных данных
    month = "2023-12"
    transactions = [
        {"Статус": "OK", "Дата операции": "2023-12-01", "Сумма платежа": -30},
        {"Статус": "OK", "Дата операции": "2023-12-15", "Сумма платежа": -25},
        {"Статус": "OK", "Дата операции": "invalid_date", "Сумма платежа": -10},
    ]
    limit = 50

    with pytest.raises(ValueError):
        investment_income(month, transactions, limit)
