import pandas as pd
from pathlib import Path
import logging
from datetime import datetime


TODAY = datetime.now().strftime("%Y-%m-%d")
PROJECT_ROOT = Path.cwd()
INPUT_FILE_PATH = Path(f"{PROJECT_ROOT}/input/sleep_efficiency__raw.csv")
OUTPUT_FOLDER = Path(f"{PROJECT_ROOT}/input/chunks")
DIVISOR = 7


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
    if delete_output_contents:
        deleted_count = delete_all_csv_from_folder(output_folder)
        logger.info(f"Deleted {deleted_count} .csv files from {output_folder}.")

    df = pd.read_csv(input_file_path)
    df_len = len(df)
    rows_per_part = df_len // divisor
    logger.info(f"# of parts : {divisor}; Rows per full part: {rows_per_part}.")

    step = 0
    for i in range(0, df_len, rows_per_part):
        step += 1
        chunk = df.iloc[i:i+rows_per_part]

        output_path = f"{output_folder}/part_{step}.csv"
        chunk.to_csv(output_path,index=False)

    logger.info(f"{input_file_path.name} was divided into {divisor} parts.")


def delete_all_csv_from_folder(path: Path) -> int:
    deleted_count = 0
    for file in path.glob("*.csv"):
        file.unlink()
        deleted_count += 1
    return deleted_count


divide_csv_into_chunks(divisor=DIVISOR, input_file_path=INPUT_FILE_PATH, output_folder=OUTPUT_FOLDER, delete_output_contents=True)