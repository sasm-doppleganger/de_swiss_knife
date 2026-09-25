import pandas as pd
from pathlib import Path
from delete_output import delete_all_csv_from_folder


INPUT_PATH = Path("input/sleep_efficiency__raw.csv")
OUTPUT_FOLDER = Path("input/chunks")
PARTS = 12


# EXTRA CAREFUL WITH delete_output_contents
# DELETES ALL .csv files beforehand in output folder if True
def divide_csv_into_chunks(divisor:int, input_file_path:str, output_folder:str, delete_output_contents:bool):
    if delete_output_contents:
        delete_all_csv_from_folder(output_folder)
        print(f"Deleted all .csv from {output_folder}")

    df = pd.read_csv(input_file_path)
    df_len = len(df)
    rows_per_part = df_len // divisor

    print(f"PARTS: {divisor}")
    print(f"ROWS PER PART: {rows_per_part}")

    step = 1
    for i in range(0, df_len, rows_per_part):
        print(f"STEP: {step}")
        chunk = df.iloc[i:i+rows_per_part]

        output_path = f"{output_folder}/step_{step}.csv"
        chunk.to_csv(output_path,index=False)
        step += 1

divide_csv_into_chunks(10, INPUT_PATH, OUTPUT_FOLDER, True)




