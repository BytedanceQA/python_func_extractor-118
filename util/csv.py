import os
import csv

def save_to_csv(all_functions, directory, fieldnames):
    """ Save analyzed data to a CSV file. """
    output_file = os.path.join(directory, "dependency_analysis_results.csv")
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_functions)
    print(f"依赖分析完成。结果已保存到 {output_file}")