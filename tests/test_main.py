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

