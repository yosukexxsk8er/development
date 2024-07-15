
from gen_json_from_csv.find_files_in_folder import find_files_in_folder
import json
import re
import os

def main():
    pass

    folder = r"logs\20240714A"
    pattern = "^\d+_"
    extension = ".json"
    output_dir = "merged"
    os.makedirs(output_dir, exist_ok=True)

    file_list = find_files_in_folder(folder=folder, pattern=pattern, extension=extension)
    mapped_dict = {}
    type_order = ["setting", "result"]
    for type in type_order:
        for file in file_list:
            m = re.search(rf"^(\d+)_.*{type}.*\.json", os.path.basename(file))
            if(m):
                try:
                    mapped_dict[m.group(1)].append(file)
                except KeyError:
                    mapped_dict[m.group(1)] = [file]


    pass

    for key, mapped_file_list in mapped_dict.items():
        merged_dict = {}
        for file in mapped_file_list:
            with open(file) as f:
                merged_dict.update(json.load(f))
        with open(f"{output_dir}/merged_{key}.json", "w") as f:
            json.dump(merged_dict, f, indent=4)




if __name__ == "__main__":
    main()
