import os
import pandas as pd

def filter_openasip_instructions(filepath, folder):
    # 读取 analyse_instructions_seq1.csv 并过滤行
    df = pd.read_csv(filepath)
    filtered_df = df[df['Sequence'].str.startswith('openasip_base_')]
    # 在第一行添加model列
    filtered_df.insert(0, 'Model', folder)
    return filtered_df

def extract_report_data(filepath):
    # 读取 report.csv 并提取需要的列
    report_df = pd.read_csv(filepath, usecols=[
        'Run', 'Model', 'Frontend', 'Target',
        'Total Instructions', 'Total ROM', 'Total RAM',
        'Total Cycles (rel.)', 'Total ROM (rel.)', 'Total RAM (rel.)'
    ])
    return report_df

def process_all_folders(base_dir):
    all_reports = []  # 用于存储所有 report_data 的列表
    filtered_reports = []  # 用于存储所有 filtered_data 的列表

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)

        if os.path.isdir(folder_path):
            # 指定文件路径
            csv_file_path = os.path.join(folder_path, 'analyse_instructions_seq1.csv')
            report_file_path = os.path.join(folder_path, 'report.csv')

            if os.path.exists(csv_file_path):
                print(f"Processing analyse_instructions_seq1.csv in folder: {folder_path}")

                # 过滤 analyse_instructions_seq1.csv 中的指令
                filtered_df = filter_openasip_instructions(csv_file_path, folder)

                # 合并所有的 analyse_instructions_seq1 数据
                filtered_reports.append(filtered_df)
            else:
                print(f"analyse_instructions_seq1.csv not found in {folder_path}")

            if os.path.exists(report_file_path):
                print(f"Processing report.csv in folder: {folder_path}")

                # 提取 report.csv 中需要的字段
                report_df = extract_report_data(report_file_path)

                # 将提取的数据添加到 all_reports 列表
                all_reports.append(report_df)
            else:
                print(f"report.csv not found in {folder_path}")

    # 合并所有的 filtered_data 数据
    if filtered_reports:
        filtered_output_filepath = os.path.join(base_dir, 'filtered_data.csv')
        filtered_data_df = pd.concat(filtered_reports, ignore_index=True)
        filtered_data_df.to_csv(filtered_output_filepath, index=False)
        print(f"All filtered data saved to {filtered_output_filepath}")
    else:
        print("No filtered data to save.")

    # 合并所有的 report 数据
    if all_reports:
        merged_report_df = pd.concat(all_reports, ignore_index=True)

        # 保存合并后的结果
        merged_output_filepath = os.path.join(base_dir, 'merged_report_data.csv')
        merged_report_df.to_csv(merged_output_filepath, index=False)
        print(f"All report data merged and saved to {merged_output_filepath}")
    else:
        print("No report data to merge.")

if __name__ == "__main__":
    base_directory = os.path.expanduser('~/project/ba/results')

    process_all_folders(base_directory)
