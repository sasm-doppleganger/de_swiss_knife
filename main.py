import pandas as pd


PATH = r"input/sleep_efficiency__raw.csv"
PARTS = 12




df = pd.read_csv(PATH)
df_len = len(df)


rows_per_part = df_len // PARTS
print(f"ROWS PER PART: {rows_per_part}")

for i in range(0, df_len, rows_per_part):
    print(f"{i}:{i+rows_per_part}")