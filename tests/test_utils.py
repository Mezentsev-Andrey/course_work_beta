import datetime
import json
from typing import Any

import pandas as pd
import pytest
from freezegun import freeze_time

from config import OPERATIONS_PATH
from src.utils import (filter_operations_by_date, get_cards_payments,
                       get_converted_date, get_greeting_phrase,
                       get_top_five_operations, load_json_file, load_xlsx_file)
from tests.test_data.path_for_test import (empty_oper_path,
                                           empty_operations_path,
                                           test_operations_path)

test_date = "2021-06-23 15:00:00"


def test_load_xlsx_file_valid_file(tmp_path: Any) -> None:
    # Создание временного файла Excel с данными
    excel_data = {"column1": [1, 2, 3], "column2": ["a", "b", "c"]}
    file_path = tmp_path / "test_file.xlsx"
    pd.DataFrame(excel_data).to_excel(file_path, index=False)

    # Вызов функции и проверка возвращаемого значения
    result = load_xlsx_file(file_path)
    assert isinstance(result, pd.DataFrame)
    assert result.equals(pd.DataFrame(excel_data))


def test_load_xlsx_file_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_xlsx_file("nonexistent_file.xlsx")


def test_load_xlsx_file_value_error(tmp_path: Any) -> None:
    # Создание временного файла с некорректными данными
    file_path = tmp_path / "invalid_file.xlsx"
    with open(file_path, "w") as f:
        f.write("invalid_data")

    # Проверка генерации ValueError
    with pytest.raises(ValueError):
        load_xlsx_file(file_path)


def test_load_json_file_valid_file(tmp_path: Any) -> None:
    # Создание временного файла JSON с данными
    json_data = {"key": "value", "number": 42}
    file_path = tmp_path / "test_file.json"
    with open(file_path, "w") as f:
        json.dump(json_data, f)

    # Вызов функции и проверка возвращаемого значения
    result = load_json_file(file_path)
    assert isinstance(result, dict)
    assert result == json_data


def test_load_json_file_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_json_file("nonexistent_file.json")


def test_load_json_file_json_decode_error(tmp_path: Any) -> None:
    # Создание временного файла с некорректными данными
    file_path = tmp_path / "invalid_file.json"
    with open(file_path, "w") as f:
        f.write("invalid_data")

    # Проверка генерации JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        load_json_file(file_path)


def test_get_converted_date_valid_date() -> None:
    # Проверка успешного преобразования строки с датой
    date_string = "2023-12-06 12:34:56"
    result = get_converted_date(date_string)
    expected_date = datetime.datetime(2023, 12, 6, 12, 34, 56)
    assert result == expected_date


def test_get_converted_date_invalid_date() -> None:
    # Проверка генерации ValueError при некорректной строке с датой
    invalid_date_string = "invalid_date"
    with pytest.raises(ValueError):
        get_converted_date(invalid_date_string)


def test_filter_operations_by_date_error() -> None:
    assert len(filter_operations_by_date(load_xlsx_file(OPERATIONS_PATH), get_converted_date(test_date))) == 120
    with pytest.raises(ValueError):
        assert filter_operations_by_date(load_xlsx_file(test_operations_path), get_converted_date(test_date))
    with pytest.raises(KeyError):
        assert filter_operations_by_date(load_xlsx_file(empty_operations_path), get_converted_date(test_date))


@pytest.fixture
def test_operations() -> pd.DataFrame:
    data = {
        "Номер карты": ["1234", "5678", "9034"],
        "Сумма операции": [-100, -200, 300],
        "Валюта операции": ["RUB", "RUB", "USD"],
    }
    return pd.DataFrame(data)


def test_get_cards_payments(test_operations: Any, caplog: Any) -> None:
    # Используем фикстуру test_operations как входные данные для функции
    result = get_cards_payments(test_operations)
    # Проверяем, что функция возвращает список словарей
    assert isinstance(result, list)
    # Проверяем, что результат содержит ожидаемое количество элементов
    assert len(result) == 3

    # Проверяем, что каждый элемент результата является словарем
    for card_dict in result:
        assert isinstance(card_dict, dict)
    # Проверяем, что логгер не содержит ошибок
    assert "Произошла ошибка" not in caplog.text


def test_get_cards_payments_error() -> None:
    with pytest.raises(KeyError):
        assert get_cards_payments(load_xlsx_file(empty_operations_path))
    with pytest.raises(TypeError):
        assert get_cards_payments(empty_oper_path, False)  # type: ignore


@pytest.fixture
def sample_operations() -> pd.DataFrame:
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
def test_get_top_five_operations(sample_operations: Any, caplog: Any) -> None:
    result = get_top_five_operations(sample_operations)
    # Проверяем, что результат не пустой
    assert result
    # Проверяем, что результат - список
    assert isinstance(result, list)
    # Проверяем, что в списке 5 элементов
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


def test_get_top_five_operations_error() -> None:
    assert len(get_top_five_operations(load_xlsx_file(OPERATIONS_PATH))) == 5
    with pytest.raises(KeyError):
        assert get_top_five_operations(load_xlsx_file(empty_operations_path))
    with pytest.raises(TypeError):
        assert get_top_five_operations(empty_oper_path, False)  # type: ignore


@freeze_time("2021-10-16 03:00:00")
def test_get_greeting_phrase_night() -> None:
    assert get_greeting_phrase() == "Доброй ночи!"


@freeze_time("2021-10-16 10:00:00")
def test_get_greeting_phrase_morning() -> None:
    assert get_greeting_phrase() == "Доброе утро!"


@freeze_time("2021-10-16 15:00:00")
def test_get_greeting_phrase_day() -> None:
    assert get_greeting_phrase() == "Добрый день!"


@freeze_time("2021-10-16 21:00:00")
def test_get_greeting_phrase_evening() -> None:
    assert get_greeting_phrase() == "Добрый вечер!"
