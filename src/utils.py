"""
Utility functions for file handling and system operations.
"""
import os
from datetime import datetime

def save_to_file(device_name, content):
    """
    Saves text content to a file with a timestamp.
    Structure: backups/YYYY-MM-DD/device_name_time.txt
    """
    # 1. Create a timestamp
    now = datetime.now()
    date_folder = now.strftime("%Y-%m-%d")
    time_stamp = now.strftime("%H-%M-%S")

    # 2. Define the path: backups/2023-10-25/
    folder_path = os.path.join("backups", date_folder)

    # 3. Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 4. Write the file
    filename = f"{device_name}_{time_stamp}.txt"
    full_path = os.path.join(folder_path, filename)

    # Pylint W1514: Always specify encoding
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return full_path