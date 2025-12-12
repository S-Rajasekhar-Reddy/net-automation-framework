"""
Module: Network Guardian (State Validator)
Purpose: Compares two network states (pre/post change) to ensure stability.
"""
import difflib
import os
from datetime import datetime

class StateValidator:
    """
    Compares configuration or state files to find differences.
    """
    def save_snapshot(self, device_name, content, tag="snapshot"):
        """Saves a state to snapshots/device_tag_timestamp.txt"""
        folder = "snapshots"
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{folder}/{device_name}_{tag}_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return filename

    def compare_files(self, file1, file2):
        """Returns the difference between two files."""
        if not os.path.exists(file1) or not os.path.exists(file2):
            return "❌ Error: One or both files not found."

        with open(file1, 'r', encoding="utf-8") as f1, open(file2, 'r', encoding="utf-8") as f2:
            f1_lines = f1.readlines()
            f2_lines = f2.readlines()

        diff = difflib.unified_diff(
            f1_lines, f2_lines, 
            fromfile='Pre-Change', tofile='Post-Change', lineterm=''
        )
        
        # Convert generator to string
        diff_text = "\n".join(list(diff))
        return diff_text if diff_text else "✅ No Changes Detected (Stable)"