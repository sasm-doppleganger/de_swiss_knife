import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
from datacontract.data_contract import DataContract
import duckdb
import uuid


TODAY = datetime.now().strftime("%Y-%m-%d")

PROJECT_ROOT = Path.cwd()
DATA_CONTRACT_LOCATION = Path(f"{PROJECT_ROOT}/input/data_contract.yaml")
INPUT_FILE_PATH = Path(f"{PROJECT_ROOT}/input/sleep_efficiency__raw.csv")
OUTPUT_FOLDER = Path(f"{PROJECT_ROOT}/input/chunks")
DIVISOR = 11


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
    # DataContract class can't accept Path, needs to be converted to str
    data_contract = DataContract(data_contract_file=str(data_contract_file_path),
                                 )

    lint = data_contract.lint()

    if not lint.has_passed():
        raise ValueError("Data contract linting failed")    
    logger.info("Data contract lint has been passed")

    run = data_contract.test()

    if not run.has_passed():
        for check in run.checks:
            if check.result.value != "passed":
                logger.error(f"[{check.result.value.upper()}] {check.name}")
        raise ValueError("Data contract is violated")

    logger.info("Data contract test has been passed")


def summarize_file_ingestion(): 
    with duckdb.connect() as con:
        con.read_csv(INPUT_FILE_PATH).to_table("csv_input")
        input_table = con.table("csv_input")

        # TEMPORARY SOLUTION FOR DB
        con.sql("""
            CREATE TABLE ingestion_summary_table (
                ingestion_id UUID,
                pipeline_run_id UUID,

                -- File identity
                file_name VARCHAR,
                file_path VARCHAR,
                file_extension VARCHAR,
                file_size_bytes UINTEGER,
                file_modified_at TIMESTAMP,

                -- Ingestion timing
                discovered_at TIMESTAMP,
                ingestion_started_at TIMESTAMP,
                ingestion_completed_at TIMESTAMP,

                -- Processing
                status VARCHAR,
                rows_read USMALLINT,
                rows_written USMALLINT,
                rows_rejected USMALLINT,

                -- Source / destination
                source_system VARCHAR,
                destination_table VARCHAR,

                -- Schema
                schema_version VARCHAR,
                column_count USMALLINT,

                -- Error information
                error_type VARCHAR,
                error_message VARCHAR,

                -- Pipeline information
                pipeline_name VARCHAR,
                pipeline_version VARCHAR
            )
        """)

        summary_table = con.table("ingestion_summary_table")

        # FILLING INFORMATION
        data = {
            "ingestion_id": uuid.uuid4(),
            "pipeline_run_id": uuid.uuid4(),

            #file identity
            "file_name": INPUT_FILE_PATH.stem,
            "file_path": str(INPUT_FILE_PATH),
            "file_extension": INPUT_FILE_PATH.suffix,
            "file_size_bytes": INPUT_FILE_PATH.stat().st_size,
            "file_modified_at": datetime.fromtimestamp(INPUT_FILE_PATH.stat().st_mtime),

            # ingestion timing
            "discovered_at": datetime.now(),
            "ingestion_started_at": datetime.now(),
            # "ingestion_completed_at": TO_DO,

            # processing
            # "status": TO_DO,
            "rows_read": input_table.shape[0],
            # "rows_written": TO_DO,
            # "rows_rejected": TO_DO,

            # source/destination
            # "source_system": TO_DO,
            # "destination_table": TO_DO,
            
            # schema
            # "schema_version": TO_DO,
            "column_count": input_table.shape[1],

            # errors
            # "error_type": TO_DO,
            # "error_message": TO_DO,

            # pipeline information
            # "pipeline_name": TO_DO,
            # "pipeline_version": TO_DO,
        }

        # INSERTION

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))

        con.execute(f"""
            INSERT INTO ingestion_summary_table ({columns})
            VALUES ({placeholders})
            """,
            list(data.values())
                    )

        # INSPECTION
        df = con.sql("""
            SELECT *
            FROM ingestion_summary_table
        """).fetchdf()

        print(df.T.to_string(header=False))
        print(input_table.shape[1])
                

# def quarantine_bad_rows():
#     with open(DATA_CONTRACT_LOCATION, "r", encoding="utf-8") as f:
#         data = yaml.safe_load(f)

#     print(data['schema'])
    

if __name__ == "__main__":
    # divide_csv_into_chunks(divisor=DIVISOR,
    #                        input_file_path=INPUT_FILE_PATH,
    #                        output_folder=OUTPUT_FOLDER,
    #                        delete_output_contents=True)

    # data_contract_validation(
    #     DATA_CONTRACT_LOCATION
    # )


    summarize_file_ingestion()

    # normalize_csv_to_df()

    # quarantine_bad_rows()