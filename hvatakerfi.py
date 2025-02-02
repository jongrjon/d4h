import requests
import pandas as pd
import datetime

# Constants
BASE_URL = "https://api.team-manager.us.d4h.com/v3"

# User Inputs
api_key = input("Enter your D4H Personal Access Token: ")
tags_input = input("Enter tags (comma-separated): ")
tags = [tag.strip() for tag in tags_input.split(',')]
headers = {"Authorization": f"Bearer {api_key}"}

def validate_token():
    """Check if the API token is valid."""
    response = requests.get(f"{BASE_URL}/whoami", headers=headers)
    if response.status_code == 401:
        print("Error: Invalid or legacy token detected. Please use a valid Personal Access Token (PAT).")
        exit(1)
    elif response.status_code != 200:
        print(f"Unexpected authentication error: {response.text}")
        exit(1)

def get_team_id():
    """Retrieve the team ID from the API."""
    response = requests.get(f"{BASE_URL}/whoami", headers=headers)
    if response.status_code == 200:
        return response.json()['members'][0]['owner']['id']
    else:
        print("Error retrieving team ID:", response.text)
        return None

def get_tag_ids(team_id, tags):
    """Retrieve tag IDs based on tag names."""
    response = requests.get(f"{BASE_URL}/team/{team_id}/tags", headers=headers)
    if response.status_code == 200:
        available_tags = response.json().get("results", [])
        tag_map = {tag["title"]: tag["id"] for tag in available_tags}
        return {tag: tag_map.get(tag) for tag in tags if tag in tag_map}
    else:
        print("Error retrieving tags:", response.text)
        return {}

def get_attendance_for_event(team_id, event_id, endpoint):
    """Retrieve attendance details for a specific event."""
    response = requests.get(
        f"{BASE_URL}/team/{team_id}/{endpoint}/{event_id}/attendance", headers=headers
    )
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error retrieving attendance for event {event_id}: {response.text}")
        return []

def get_events_for_tag(team_id, tag_id, endpoint):
    """Retrieve events, incidents, and exercises by tag ID."""
    two_years_ago = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=730)).isoformat()
    response = requests.get(
        f"{BASE_URL}/team/{team_id}/{endpoint}?tag_id={tag_id}&after={two_years_ago}", headers=headers
    )
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error retrieving {endpoint} for tag ID {tag_id}: {response.text}")
        return []

def get_attendance_data(team_id, tag_ids):
    """Fetch attendance data for each tag across events, incidents, and exercises."""
    attendance_data = {}
    
    for tag_name, tag_id in tag_ids.items():
        if tag_id is None:
            print(f"Warning: Tag '{tag_name}' not found in available tags.")
            continue
        
        for endpoint in ["events", "incidents", "exercises"]:
            events = get_events_for_tag(team_id, tag_id, endpoint)
            for event in events:
                event_id = event["id"]
                attendance_list = get_attendance_for_event(team_id, event_id, endpoint)
                for attendee in attendance_list:
                    member_name = attendee["name"]
                    time_spent = attendee.get("minutes", 0)
                    if member_name not in attendance_data:
                        attendance_data[member_name] = {}
                    attendance_data[member_name][tag_name] = attendance_data[member_name].get(tag_name, 0) + time_spent
    
    return attendance_data

def generate_excel_report(attendance_data, tags):
    """Generate an Excel report from the collected data."""
    df = pd.DataFrame.from_dict(attendance_data, orient='index', columns=tags).fillna(0)
    df.to_excel("attendance_report.xlsx")
    print("Report saved as attendance_report.xlsx")

validate_token()  # Ensure token is valid
team_id = get_team_id()
if team_id:
    tag_ids = get_tag_ids(team_id, tags)
    attendance_data = get_attendance_data(team_id, tag_ids)
    generate_excel_report(attendance_data, tags)
