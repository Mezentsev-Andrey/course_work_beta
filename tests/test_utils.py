import datetime
import json

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (get_cards_payments, get_converted_date,
                       get_greeting_phrase, get_top_five_operations,
                       load_json_file, load_xlsx_file)


def test_load_xlsx_file_valid_file(tmp_path):
    # Создание временного файла Excel с данными
    excel_data = {"column1": [1, 2, 3], "column2": ["a", "b", "c"]}
    file_path = tmp_path / "test_file.xlsx"
    pd.DataFrame(excel_data).to_excel(file_path, index=False)

    # Вызов функции и проверка возвращаемого значения
    result = load_xlsx_file(file_path)
    assert isinstance(result, pd.DataFrame)
    assert result.equals(pd.DataFrame(excel_data))


def test_load_xlsx_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_xlsx_file("nonexistent_file.xlsx")


def test_load_xlsx_file_value_error(tmp_path):
    # Создание временного файла с некорректными данными
    file_path = tmp_path / "invalid_file.xlsx"
    with open(file_path, "w") as f:
        f.write("invalid_data")

    # Проверка генерации ValueError
    with pytest.raises(ValueError):
        load_xlsx_file(file_path)


def test_load_json_file_valid_file(tmp_path):
    # Создание временного файла JSON с данными
    json_data = {"key": "value", "number": 42}
    file_path = tmp_path / "test_file.json"
    with open(file_path, "w") as f:
        json.dump(json_data, f)

    # Вызов функции и проверка возвращаемого значения
    result = load_json_file(file_path)
    assert isinstance(result, dict)
    assert result == json_data


def test_load_json_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_json_file("nonexistent_file.json")


def test_load_json_file_json_decode_error(tmp_path):
    # Создание временного файла с некорректными данными
    file_path = tmp_path / "invalid_file.json"
    with open(file_path, "w") as f:
        f.write("invalid_data")

    # Проверка генерации JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        load_json_file(file_path)


def test_get_converted_date_valid_date():
    # Проверка успешного преобразования строки с датой
    date_string = "2023-12-06 12:34:56"
    result = get_converted_date(date_string)
    expected_date = datetime.datetime(2023, 12, 6, 12, 34, 56)
    assert result == expected_date


def test_get_converted_date_invalid_date():
    # Проверка генерации ValueError при некорректной строке с датой
    invalid_date_string = "invalid_date"
    with pytest.raises(ValueError):
        get_converted_date(invalid_date_string)


@pytest.fixture
def test_operations():
    # Замените этот блок кода на создание тестовых данных
    data = {
        "Номер карты": ["1234", "5678", "1234"],
        "Сумма операции": [-100, -200, 300],
        "Валюта операции": ["RUB", "RUB", "USD"],
    }
    return pd.DataFrame(data)


# Тест для функции get_cards_payments
def test_get_cards_payments(test_operations, caplog):
    # Используем фикстуру test_operations как входные данные для функции
    result = get_cards_payments(test_operations)

    # Проверяем, что функция возвращает список словарей
    assert isinstance(result, list)

    # Проверяем, что результат содержит ожидаемое количество элементов
    assert len(result) == 2

    # Проверяем, что каждый элемент результата является словарем
    for card_dict in result:
        assert isinstance(card_dict, dict)

    # Проверяем, что логгер не содержит ошибок
    assert "Ошибка" not in caplog.text


@pytest.fixture
def sample_operations():
    data = {
        "Дата операции": [
            "2023-01-01",
            "2023-01-02",
            "2023-01-03",
            "2023-01-04",
            "2023-01-05",
        ],
        "Сумма операции": [-100, -200, -300, -400, -500],
        "Валюта операции": ["RUB"] * 5,
        "Номер карты": ["1234", "4567", "7890", "1234", "4567"],
        "Категория": ["Food", "Shopping", "Entertainment", "Food", "Shopping"],
        "Описание": ["McDonald's", "Amazon", "Movie", "Burger King", "eBay"],
    }
    return pd.DataFrame(data)


# Написание тестов
def test_get_top_five_operations(sample_operations, caplog):
    result = get_top_five_operations(sample_operations)

    # Проверяем, что результат не пустой
    assert result

    # Проверяем, что результат - список
    assert isinstance(result, list)

    # Проверяем, что в списке 2 элемента (в зависимости от данных)
    assert len(result) == 5

    # Проверяем структуру каждого элемента списка
    for operation in result:
        assert isinstance(operation, dict)
        assert "date" in operation
        assert "amount" in operation
        assert "category" in operation
        assert "description" in operation

    # Проверяем, что логирование успешно выполнено
    assert "Топ-5 операций успешно получены." in caplog.text

    # Проверяем, что логирование ошибок не произошло
    assert "Ошибка при получении топ-5 операций." not in caplog.text


@freeze_time("2021-10-16 03:00:00")
def test_get_greeting_phrase_night():
    assert get_greeting_phrase() == "Доброй ночи!"


@freeze_time("2021-10-16 10:00:00")
def test_get_greeting_phrase_morning():
    assert get_greeting_phrase() == "Доброе утро!"


@freeze_time("2021-10-16 15:00:00")
def test_get_greeting_phrase_day():
    assert get_greeting_phrase() == "Добрый день!"


@freeze_time("2021-10-16 21:00:00")
def test_get_greeting_phrase_evening():
    assert get_greeting_phrase() == "Добрый вечер!"
