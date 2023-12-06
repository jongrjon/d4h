import pandas as pd
import json

# Define the path to the JSON file
json_file_path = "sulur_felagar.json"

# Read JSON data from the file
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract "name" and "id" values from the "data" array
data_list = data.get("data", [])

name_id_data = [{"name": item.get("name"), "id": item.get("id")} for item in data_list]

# Create a DataFrame from the extracted data
df = pd.DataFrame(name_id_data)

# Save the DataFrame to an Excel file
output_excel_file = "output_data.xlsx"
df.to_excel(output_excel_file, index=False)

print("Data extracted and saved to Excel file.")