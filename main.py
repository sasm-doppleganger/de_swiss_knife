import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
from datacontract.data_contract import DataContract


TODAY = datetime.now().strftime("%Y-%m-%d")

PROJECT_ROOT = Path.cwd()
DATA_CONTRACT_LOCATION = Path(f"{PROJECT_ROOT}/input/data_contract.yaml")
INPUT_FILE_PATH = Path(f"{PROJECT_ROOT}/input/sleep_efficiency__raw.csv")
OUTPUT_FOLDER = Path(f"{PROJECT_ROOT}/input/chunks")
DIVISOR = 10


# log_dir = PROJECT_ROOT / "logs" / "local_scraper"
# log_dir.mkdir(exist_ok=True)
# log_file = log_dir / f"scraper_{TODAY}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    # handlers=[logging.FileHandler(log_file),
    #           logging.StreamHandler()],
    force=True
)
logger = logging.getLogger(__name__)



# This function is needed to ease dividing a .csv file to test incremental loading 
#
# EXTRA CAREFUL WITH delete_output_contents
# DELETES ALL .csv files beforehand in output folder if True
def divide_csv_into_chunks(divisor:int, input_file_path:str, output_folder:str, delete_output_contents:bool):
    if isinstance(divisor, bool) or not isinstance(divisor, int):
        raise TypeError(f"Expected an int, but got {type(divisor).__name__}")

    if divisor <= 0:
        raise ValueError("Divisor must be greater than 0")

    if delete_output_contents:
        deleted_count = delete_all_csv_from_folder(output_folder)
        logger.info(f"Deleted {deleted_count} .csv files from {output_folder}.")

    df = pd.read_csv(input_file_path)

    if df.empty:
        raise ValueError("Input CSV contains no rows")

    df_len = len(df)

    if divisor > df_len:
        raise ValueError(f"Divisor ({divisor}) cannot be greater than the number of rows ({df_len})")

    rows_per_part = df_len // divisor
    logger.info(f"# of parts : {divisor}; Rows per full part: {rows_per_part}.")

    step = 0
    for i in range(0, df_len, rows_per_part):
        step += 1
        chunk = df.iloc[i:i+rows_per_part]
        
        if i + rows_per_part > df_len:
            # append to previous file
            output_path = f"{output_folder}/part_{step-1}.csv"
            chunk.to_csv(output_path,index=False, mode='a', header=False)
            break

        output_path = f"{output_folder}/part_{step}.csv"
        chunk.to_csv(output_path,index=False)

    logger.info(f"{input_file_path.name} was succesfully divided.")


def delete_all_csv_from_folder(path: Path) -> int:
    deleted_count = 0
    for file in path.glob("*.csv"):
        file.unlink()
        deleted_count += 1
    return deleted_count


def data_contract_validation(data_contract_file_path: Path):
    data_contract = DataContract(data_contract_file=data_contract_file_path)

    run = data_contract.test()
    if not run.has_passed():
        for check in run.checks:
            if check.result.value != "passed":
                print(" ")
                print(check.name)
                print(check.result)
                print(check.reason) 
        raise ValueError("Data contract is violated")
    


if __name__ == "__main__":
    data_contract_validation(
        Path("input/chunks/part_1.csv"),
        DATA_CONTRACT_LOCATION
    )
