
from gen_json_from_csv.find_files_in_folder import find_files_in_folder

def main():
    pass

    folder = r"logs\20240714A"
    pattern = "01"
    extension = ".json"
    file_list = find_files_in_folder(folder=folder, pattern=pattern, extension=extension)
    pass



if __name__ == "__main__":
    main()
