#!/usr/bin/env python3

import csv
from pathlib import Path

def test_append():
    # Create test data
    test_data = [
        {"id": "3", "name": "test3", "value": "300"},
        {"id": "4", "name": "test4", "value": "400"}
    ]
    
    # Path to the test file
    output_path = Path("test_output2.csv")
    
    # Get the keys from the test data
    keys = set()
    for item in test_data:
        keys.update(item.keys())
    
    # Sort the keys for consistent output
    sorted_keys = sorted(keys)
    
    # Check if the file exists
    file_exists = output_path.exists()
    print(f"Output file {output_path} exists: {file_exists}")
    
    if file_exists:
        # Read existing data to get headers
        existing_headers = []
        try:
            with open(output_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                existing_headers = reader.fieldnames or []
            print(f"Existing file has {len(existing_headers)} columns: {existing_headers}")
            
            # Merge headers
            for header in existing_headers:
                if header not in sorted_keys:
                    sorted_keys.append(header)
            
            # Check if the file ends with a newline
            with open(output_path, 'r') as f:
                f.seek(0, 2)  # Go to the end of the file
                if f.tell() > 0:  # If file is not empty
                    f.seek(f.tell() - 1, 0)  # Go to the last character
                    last_char = f.read(1)
                    needs_newline = last_char != '\n'
                    print(f"File needs newline: {needs_newline}")
            
            # Append the results to the CSV file
            with open(output_path, 'a', newline='') as f:
                # Add a newline if needed to prevent data corruption
                if needs_newline:
                    f.write('\n')
                writer = csv.DictWriter(f, fieldnames=sorted_keys)
                writer.writerows(test_data)
            
            print(f"Appended {len(test_data)} results to existing file {output_path}")
            return
        except Exception as e:
            print(f"Error reading or appending to existing file: {e}")
            # If there's an error, fall back to overwriting
            print("Falling back to creating a new file")
            file_exists = False
    
    # If file doesn't exist or we had an error, create a new file
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted_keys)
        writer.writeheader()
        writer.writerows(test_data)
    
    print(f"Created new file with {len(test_data)} results at {output_path}")

if __name__ == "__main__":
    test_append()