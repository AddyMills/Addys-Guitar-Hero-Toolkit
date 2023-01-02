import os



if __name__ == "__main__":
    dir_1 = f".\\input QB"
    dir_2 = f".\\output\\Text"

    for file in os.listdir(dir_1):
        if not file.endswith(".qb.xen"):
            continue
        filepath_1 = os.path.join(dir_1, file)
        filepath_2 = os.path.join(dir_2, file)
        file_name_1 = file[:-4]

        with open(filepath_1, "rb") as f:
            file_1 = f.read()
        try:
            with open(filepath_2, "rb") as f:
                file_2 = f.read()
        except:
            print(f"File {file_name_1} not found in output folder. Skipping...")
            continue

        if file_1[28:] != file_2[28:]:
            print(f"{file_name_1}: No match!")
        """else:
            print(f"{file_name_1}: Match!")"""