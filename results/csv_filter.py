import os
import pandas as pd

def filter_openasip_instructions(filepath):

    df = pd.read_csv(filepath)

    filtered_df = df[df['Sequence'].str.startswith('openasip_base_')]

    return filtered_df

def process_all_folders(base_dir):

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)

        if os.path.isdir(folder_path):
            csv_file_path = os.path.join(folder_path, 'analyse_instructions_seq1.csv')

            if os.path.exists(csv_file_path):
                print(f"Processing file: {csv_file_path}")

                filtered_df = filter_openasip_instructions(csv_file_path)

                output_filepath = os.path.join(base_dir, f'{folder}.csv')
                filtered_df.to_csv(output_filepath, index=False)
                print(f"Filtered instructions saved to {output_filepath}")
            else:
                print(f"CSV file not found in {folder_path}")

if __name__ == "__main__":
    base_directory = os.path.expanduser('~/project/ba/results')

    process_all_folders(base_directory)
