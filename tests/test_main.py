import pandas as pd
import pytest

from main import divide_csv_into_chunks


def test_fivide_csv_into_chunks(tmp_path):
    input_file = tmp_path/"input.csv"
    output_folder = tmp_path/"chunks"
    output_folder.mkdir()

    df = pd.DataFrame({
        "id": range(10),
        "value": range(10,20)
    })

    df.to_csv(input_file, index=False)

    divide_csv_into_chunks(
        divisor=2,
        input_file_path=input_file,
        output_folder=output_folder,
        delete_output_contents=False
    )

    part_1 = pd.read_csv(output_folder/"part_1.csv")
    part_2 = pd.read_csv(output_folder/"part_2.csv")

    assert len(part_1) == 5
    assert len(part_2) == 5
    assert list(part_1["id"]) == [0, 1, 2, 3, 4]
    assert list(part_2["id"]) == [5, 6, 7, 8, 9]


def test_divisor_must_be_integer(tmp_path):
    input_file = tmp_path / "input.csv"
    output_folder = tmp_path / "chunks"
    output_folder.mkdir()

    pd.DataFrame({"id": range(10)}).to_csv(input_file, index=False)

    with pytest.raises(TypeError):
        divide_csv_into_chunks(
            divisor=2.5,
            input_file_path=input_file,
            output_folder=output_folder,
            delete_output_contents=False
        )


def test_divisor_must_be_positive(tmp_path):
    input_file = tmp_path / "input.csv"
    output_folder = tmp_path / "chunks"
    output_folder.mkdir()

    pd.DataFrame({"id": range(10)}).to_csv(input_file, index=False)

    with pytest.raises(ValueError):
        divide_csv_into_chunks(
            divisor=0,
            input_file_path=input_file,
            output_folder=output_folder,
            delete_output_contents=False
        )


def test_divisor_cannot_exceed_row_count(tmp_path):
    input_file = tmp_path / "input.csv"
    output_folder = tmp_path / "chunks"
    output_folder.mkdir()

    pd.DataFrame({"id": range(5)}).to_csv(input_file, index=False)

    with pytest.raises(ValueError):
        divide_csv_into_chunks(
            divisor=10,
            input_file_path=input_file,
            output_folder=output_folder,
            delete_output_contents=False
        )