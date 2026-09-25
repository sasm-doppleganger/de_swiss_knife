def delete_all_csv_from_folder(path) -> int:
    deleted_count = 0
    for file in path.glob("*.csv"):
        file.unlink()
        deleted_count += 1
    return deleted_count