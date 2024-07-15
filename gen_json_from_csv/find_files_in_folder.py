import os
def find_files_in_folder(folder, pattern, extension):
    """
    Find files in a folder that match a specific pattern and extension.
    
    Args:
        folder (str): The folder path to search in.
        pattern (str): The specific pattern to match in the file names.
        extension (str): The specific extension to match in the file names.
    
    Returns:
        list: A list of file paths that match the pattern and extension.
    """
    matched_files = []
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            if pattern in file and file.endswith(extension):
                matched_files.append(os.path.join(root, file))
    
    return matched_files