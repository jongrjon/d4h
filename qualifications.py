import pandas as pd
import requests
from datetime import datetime

# Define API endpoint
base_api_url = "https://api.d4h.org/v2/team/qualifications/"
bearer_token = XXXX
# Read Excel data into a DataFrame
excel_file = "namsk.xlsx"  # Provide the path to your Excel file
df = pd.read_excel(excel_file)

# Iterate through the DataFrame
for index, row in df.iterrows():
    user_id = row['D4H NR']
    for col in df.columns[1:]:  # Skip the first column (User IDS)
        achievement_id = col
        date_value = row[col]

        # Check if date_value is a string
        if isinstance(date_value, str):
            date_values = date_value.split("/")  # Split dates by "/"
            
            # Process each date in the array
            for date_value in date_values:
                achievement_date = date_value.strip()  # Remove leading/trailing spaces

                # Check if achievement_date is a valid date
                try:
                    date_obj = datetime.strptime(achievement_date, "%d.%m.%y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")  # Format as "YYYY-MM-DD"
                except ValueError:
                    continue  # Skip invalid dates

                # Construct the complete API URL with AchievementID
                api_url = f"{base_api_url}/{achievement_id}/qualified-members"

                # Print the formatted request data in the desired format
                #formatted_request = f"POST {api_url}?member_id={user_id}&start_date={formatted_date}"
                #print(formatted_request)

                # Make a POST request to the API
                headers = {
                	"Authorization": f"Bearer {bearer_token}"
                }
                data = {
	                "member_id": user_id,
	                "start_date": formatted_date  # Use the formatted date
            	}
                response = requests.post(api_url, headers=headers, data=data)

                 # Handle the response as needed
                if response.status_code == 200:
                    print(f"Successfully sent data for User ID {user_id}, Achievement ID {achievement_id}, Date {formatted_date}")
                else:
                    print(f"Error sending data for User ID {user_id}, Achievement ID {achievement_id}, Date {formatted_date}")
                    print(f"Response Message: {response.text}")