import pandas as pd

def csv_to_excel(csv_file_path, excel_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Write the DataFrame to an Excel file
    df.to_excel(excel_file_path, index=False)

if __name__ == "__main__":
    # Input the path to the CSV file
    csv_file_path = input("Enter the path to the CSV file: ")
    
    # Input the desired path for the Excel file
    excel_file_path = input("Enter the path to save the Excel file (including the filename and .xlsx extension): ")
    
    # Convert CSV to Excel
    csv_to_excel(csv_file_path, excel_file_path)
    
    print(f"CSV file has been successfully converted to Excel file at {excel_file_path}")
