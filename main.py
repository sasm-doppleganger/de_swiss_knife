import pandas as pd


PATH = r"input/sleep_efficiency__raw.csv"
PARTS = 12




df = pd.read_csv(PATH)
df_len = len(df)


rows_per_part = df_len // PARTS
print(f"ROWS PER PART: {rows_per_part}")

start_index = 0
end_index = rows_per_part - 1

step = 0
while end_index < df_len:
    step += 1
    print(f"STEP: {step}")

    
    
    part_index = [start_index, end_index]
    print(part_index)
    end_index += rows_per_part
    start_index += rows_per_part

print(f"STEP: {step}")
part_index = [start_index, ":"]
print(part_index)