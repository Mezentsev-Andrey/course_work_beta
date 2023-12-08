import os
from pathlib import Path

import pandas as pd
import pytest

from config import OPERATIONS_PATH
from src.reports import filter_transactions, report_to_file
from src.utils import load_xlsx_file
from tests.test_data.path_for_test import empty_oper_path, test_operations_path


def test_filter_transactions() -> None:
    assert filter_transactions(load_xlsx_file(OPERATIONS_PATH), "Детские товары", "2021-10-15 16:00:00").shape == (
        4,
        15,
    )
    assert filter_transactions(load_xlsx_file(OPERATIONS_PATH), "Детские товары").shape == (0, 15)
    with pytest.raises(ValueError):
        assert filter_transactions(load_xlsx_file(OPERATIONS_PATH), "Детские товары", "2021-45-45 16:00:00")
    with pytest.raises(KeyError):
        assert filter_transactions(
            load_xlsx_file(test_operations_path),
            "Детские товары",
            "2021-10-15 16:00:00",
        )
    with pytest.raises(TypeError):
        assert filter_transactions(empty_oper_path, False)


def test_report_to_file_with_filename():
    filename = Path(__file__).parent.parent.joinpath("tests", "test_data", "test_report_filename.csv")
    if os.path.exists(filename):
        os.remove(filename)

    @report_to_file(filename=filename)
    def func(df):
        return df

    input_df = func(load_xlsx_file(OPERATIONS_PATH))

    output_df = pd.read_csv(filename, delimiter=",", encoding="utf-8")

    assert input_df.shape == output_df.shape
