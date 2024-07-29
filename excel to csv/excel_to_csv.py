import pandas as pd

def excel_to_csv(excel_file_path, sheet_name, csv_file_path):
    # Read the Excel file
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    # Convert the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print(f"Excel file '{excel_file_path}' has been converted to CSV file '{csv_file_path}'")

# Example usage
excel_file_path = 'example.xlsx'
sheet_name = 'Sheet1'
csv_file_path = 'output.csv'

excel_to_csv(excel_file_path, sheet_name, csv_file_path)
