import os
import pandas as pd

def split_csv(file_path, prefix="new_csv", chunk_size=50000):
    # Read the CSV file in chunks
    reader = pd.read_csv(file_path, chunksize=chunk_size)
    
    # Get the directory and base file name
    directory, file_name = os.path.split(file_path)
    base_name, file_extension = os.path.splitext(file_name)

    # Iterate over chunks and save each chunk to a new CSV file
    for i, chunk in enumerate(reader):
        new_file_name = f"{prefix}{i+1}.csv"
        new_file_path = os.path.join(directory, new_file_name)
        chunk.to_csv(new_file_path, index=False)
        print(f"Saved {new_file_path}")
        break

path_name = 'csv/input_csvs/zouk_point.csv'
prefix = 'zouk_point'
chunk_size = 50000
split_csv(path_name,prefix,chunk_size)