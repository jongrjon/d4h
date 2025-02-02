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
        return response.json()['members'][1]['owner']['id']
    else:
        print("Error retrieving team ID:", response.text)
        return None

def get_tag_ids(team_id, tags):
    """Retrieve tag IDs based on tag names."""
    response = requests.get(f"{BASE_URL}/team/{team_id}/tags", headers=headers)
    if response.status_code == 200:
        available_tags = response.json().get("results", [])
        print(f"Retrieved {len(available_tags)} tags from API.")
        tag_map = {tag["title"].lower(): tag["id"] for tag in available_tags}  # Normalize titles to lowercase
        found_tags = {tag: tag_map.get(tag.lower()) for tag in tags if tag.lower() in tag_map}
        print("Resolved tag IDs:", found_tags)
        
        if not found_tags:
            print("No matching tags found for provided names. Returning empty.")
            return {}
        
        return found_tags
    else:
        print("Error retrieving tags:", response.text)
        return {}

def get_member_name(team_id, member_id, member_cache):
    """Retrieve a member's name using their ID, utilizing a cache for efficiency."""
    if member_id in member_cache:
        return member_cache[member_id]
    response = requests.get(f"{BASE_URL}/team/{team_id}/members/{member_id}", headers=headers)
    if response.status_code == 200:
        member_name = response.json().get("name", "Unknown")
        member_cache[member_id] = member_name
        return member_name
    else:
        print(f"Error retrieving member info for {member_id}: {response.text}")
        return "Unknown"

def get_attendance_for_event(team_id, event_id, attendance_cache):
    """Retrieve attendance details for a specific event, caching results for efficiency."""
    if event_id in attendance_cache:
        return attendance_cache[event_id]
    response = requests.get(
        f"{BASE_URL}/team/{team_id}/attendance?activity_id={event_id}&status=ATTENDING", headers=headers
    )
    if response.status_code == 200:
        attendance_cache[event_id] = response.json().get("results", [])
        return attendance_cache[event_id]
    else:
        print(f"Error retrieving attendance for event {event_id}: {response.text}")
        return []

def get_events_for_tag(team_id, tag_id, endpoint):
    """Retrieve events, incidents, and exercises by tag ID."""
    two_years_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
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
    member_cache = {}
    attendance_cache = {}
    
    for tag_name, tag_id in tag_ids.items():
        if tag_id is None:
            print(f"Warning: Tag '{tag_name}' not found in available tags.")
            continue
        
        print(f"Fetching events for tag: {tag_name}")
        for endpoint in ["events", "incidents", "exercises"]:
            events = get_events_for_tag(team_id, tag_id, endpoint)
            print(f"Found {len(events)} {endpoint} for tag {tag_name}")
            for event in events:
                event_id = event["id"]
                print(f"Fetching attendance for event ID: {event_id}")
                attendance_list = get_attendance_for_event(team_id, event_id, attendance_cache)
                print(f"Found {len(attendance_list)} attendees for event ID: {event_id}")
                for attendee in attendance_list:
                    print("Attendee Data:", attendee)
                    member_id = attendee.get("member", {}).get("id")  # Safely get the key
                    member_name = get_member_name(team_id, member_id, member_cache)
                    start_time = datetime.datetime.fromisoformat(attendee.get("startsAt").replace("Z", "+00:00"))
                    end_time = datetime.datetime.fromisoformat(attendee.get("endsAt").replace("Z", "+00:00"))
                    time_spent = int((end_time - start_time).total_seconds() / 60)
                    if member_name not in attendance_data:
                        attendance_data[member_name] = {}
                    attendance_data[member_name][tag_name] = attendance_data[member_name].get(tag_name, 0) + (time_spent / 60)  # Convert minutes to hours
                    print(f"Added {time_spent} minutes for {member_name} under tag {tag_name}")
    
    return attendance_data

def generate_excel_report(attendance_data, tags):
    """Generate an Excel report from the collected data."""
    df = pd.DataFrame.from_dict(attendance_data, orient='index', columns=tags).fillna(0)
    print("Final attendance data:")
    print(df)
    df.to_excel("attendance_report.xlsx")
    print("Report saved as attendance_report.xlsx")

validate_token()  # Ensure token is valid
team_id = get_team_id()
if team_id:
    tag_ids = get_tag_ids(team_id, tags)
    attendance_data = get_attendance_data(team_id, tag_ids)
    generate_excel_report(attendance_data, tags)
