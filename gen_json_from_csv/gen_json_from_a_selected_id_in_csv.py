import csv
import json
import argparse
import os

def csv_to_json(input_csv, output_json, target_id):
    # Open the CSV file and read its contents
    with open(input_csv, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        
        # Read the entire CSV into a list of rows
        rows = list(reader)
        
        # Find the index of the row containing the "ID" column
        id_row_index = None
        for i, row in enumerate(rows):
            if "ID" in row:
                id_row_index = i
                break
        
        # Check if the "ID" column was found in the CSV file
        if id_row_index is None:
            raise ValueError('"ID" cell not found in the CSV file.')
        
        # Extract the settings data starting from the "ID" row
        setting_table = rows[id_row_index:]
        setting_dict = {}
        for i, setting_list in enumerate(setting_table):
            setting_dict[setting_list[0]] = setting_list[1:]

        # Convert the "ID" column values to integers
        setting_dict["ID"] = [int(x) for x in setting_dict["ID"]]
        
        # Find the index of the target ID in the "ID" column
        target_index = setting_dict["ID"].index(target_id)
        selected_dict = {}

        selected_dict["ID"] = target_id

        # Global Settings
        for row in rows[0:id_row_index]:
            if(row[0]!=""):
                selected_dict[row[0]] = row[1]

        
        # Create a dictionary with settings corresponding to the target ID
        for key, value in setting_dict.items():
            if key == "ID":
                continue
            else:
                selected_dict[key] = value[target_index]

            
        
        # Write the selected data to a JSON file
        with open(output_json, mode='w', encoding='utf-8') as json_file:
            json.dump(selected_dict, json_file, ensure_ascii=False, indent=4)

def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Convert CSV data to JSON format')
    parser.add_argument('--target_id', type=int, help='Target ID to extract from the CSV')
    parser.add_argument('--input_csv', type=str, help='Input CSV file path')
    parser.add_argument('--output_dir', type=str, help='Output directory for JSON file')
    parser.add_argument('--type_name', type=str, help='')

    # Parse the command line arguments
    args = parser.parse_args()

    # Extract arguments from the command line
    input_csv = args.input_csv
    output_dir = args.output_dir
    target_id = args.target_id
    type_name = args.type_name
    output_json_name = f"{target_id:02d}_{type_name}.json"
    output_json_path = os.path.join(output_dir, output_json_name)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Convert CSV to JSON using the specified target ID
    csv_to_json(input_csv, output_json_path, target_id)
    print(f'Created {output_json_path}')
    

if __name__ == "__main__":
    main()