from pathlib import Path

empty_operations_path = Path(__file__).parent.parent.parent.joinpath(
    "tests", "test_data", "empty_operations.xls"
)
test_operations_path = Path(__file__).parent.parent.parent.joinpath(
    "tests", "test_data", "test_operations.xls"
)
empty_json_path = Path(__file__).parent.parent.parent.joinpath(
    "tests", "test_data", "empty.json"
)
empty_oper_path = Path(__file__).parent.parent.parent.joinpath(
    "tests", "test_data", "empty_oper.xlsx"
)
broken_file_path = Path(__file__).parent.parent.parent.joinpath(
    "tests", "test_data", "broken.xls"
)
