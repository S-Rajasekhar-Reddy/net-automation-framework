import os
from datetime import datetime

def save_to_file(device_name, content):
    """
    Saves text content to a file with a timestamp.
    Structure: backups/YYYY-MM-DD/device_name_time.txt
    """
    # Create a timestamp
    now = datetime.now()
    date_folder = now.strftime("%Y-%m-%d")
    time_stamp = now.strftime("%H-%M-%S")
    
    # Define the path: backups/YYYY-MM-DD/
    folder_path = os.path.join("backups", date_folder)
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Write the file
    filename = f"{device_name}_{time_stamp}.txt"
    full_path = os.path.join(folder_path, filename)
    
    with open(full_path, "w") as f:
        f.write(content)
        
    return full_path