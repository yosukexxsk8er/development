
import os
import json
from gen_json_from_a_selected_id_in_csv.find_files_in_folder import find_files_in_folder

def merge_dict_list_by_key(dict_list):
    """
    Merge dictionaries in a list based on the same key values into arrays.
    
    Args:
        dict_list (list): A list of dictionaries to merge.
    
    Returns:
        dict: A dictionary with keys having multiple values as arrays.
    """
    merged_dict = {}
    
    for d in dict_list:
        for key, value in d.items():
            if key in merged_dict:
                if not isinstance(merged_dict[key], list):
                    merged_dict[key] = [merged_dict[key]]
                merged_dict[key].append(value)
            else:
                merged_dict[key] = value
    
    return merged_dict

def main():
    # Example usage
    folder_path = r"logs\20240714A"
    pattern_to_match = "setting"
    extension_to_match = ".json"

    matched_files_list = find_files_in_folder(folder_path, pattern_to_match, extension_to_match)
    print("\n".join(matched_files_list))

    dict_list = []
    for file_path in matched_files_list:
        with open(file_path, 'r') as f:
            dict_list.append(json.load(f))

    merged_dict = merge_dict_list_by_key(dict_list)

    pass


if __name__ == "__main__":
    main()
