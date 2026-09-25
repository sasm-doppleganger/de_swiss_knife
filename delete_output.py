def delete_all_csv_from_folder(path):
    for file in path.glob("*.csv"):
        file.unlink()