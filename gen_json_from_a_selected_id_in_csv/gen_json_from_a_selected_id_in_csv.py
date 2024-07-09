import csv
import json

def csv_to_json(input_csv, output_json, target_id):
    with open(input_csv, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        
        # Read the entire CSV into a list of rows
        rows = list(reader)
        
        # Find the "ID" row and its index
        id_row_index = None
        for i, row in enumerate(rows):
            if "ID" in row:
                id_row_index = i
                break
        
        if id_row_index is None:
            raise ValueError('"ID" cell not found in the CSV file.')
        
        # Find the target column index based on the target_id in the "ID" row
        id_row = rows[id_row_index]
        if target_id in id_row:
            target_col_index = id_row.index(target_id)
        else:
            raise ValueError(f'Target ID "{target_id}" not found in the ID row.')
        
        # Create the dictionary for JSON output
        json_data = {"ID": target_id}
        for row in rows[id_row_index + 1:]:  # Process rows below the ID row
            if row[0]:  # Skip empty rows
                key = row[0]  # First column values as keys
                value = row[target_col_index]  # Corresponding target column values
                json_data[key] = value
        
        # Write the JSON data to file
        with open(output_json, mode='w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

# Usage
input_csv = 'input.csv'
output_json = 'output.json'
target_id = '2'  # ここに指定するIDを入力してください

csv_to_json(input_csv, output_json, target_id)
