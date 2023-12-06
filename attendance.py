import http.client
import json
import math
from datetime import datetime, timedelta
import pandas as pd

#TOKEN = input("API TOKEN: ")
#GROUP = input("GROUP ID: ")

TOKEN = XXX
GROUP = "11566"

conn = http.client.HTTPSConnection("api.d4h.org")
payload = ''
headers = {
  'Authorization': 'Bearer '+TOKEN
}

elist = [562542,564437,564955,564956,564958,566775,568062,561436,569620,569622,570922,570923,571439,572710,572720,572723,572724,575714,576570,586026,586041,589065,590541,590947,590948,590983,590986,596116,597707,600383,595755,605183,606670,609063,609454,610595]

people ={}
events = {}

class Person:
    def __init__(self, name, uid):
        self.name = name
        self.id = str(uid)
        self.fundraising_hrs = 0
        self.attended =[]
        self.hrs = 0
    def __str__(self):
    	return("Name:"+self.name+" Attended: "+str(len(self.attended))+" Hrs: "+str(float(self.hrs)/60))

class Event:
	def  __init__(self, id):
		self.id = str(id)
		self.name = ""
		self. attended = {}
		self.date = datetime.now()
	def __str__(self):
		return("Event:"+self.name+" Date: "+str(self.date)+" Attended: "+str(len(self.attended)))

conn.request("GET", "/v2/team/groups/"+GROUP, payload, headers)
res = conn.getresponse()
data = res.read()
jsondata = json.loads(data)
for p in jsondata["data"]["members"]:
	conn.request("GET", "/v2/team/members/"+str(p), payload, headers)
	user_res = conn.getresponse()
	user_data = user_res.read()
	user_jason = json.loads(user_data)['data']
	user = Person(user_jason['name'], user_jason['id'])
	people[user.id]= user


for e in elist:
	conn.request("GET", "/v2/team/activities/"+str(e), payload, headers)
	res = conn.getresponse()
	data = res.read()
	jsondata = json.loads(data)['data']
	event = Event(str(e))
	print(jsondata)
	event.name = jsondata['ref_desc']
	event.date = jsondata['date']
	conn.request("GET", "https://api.d4h.org/v2/team/attendance?activity_id="+str(e)+"&status=attending", payload, headers)
	eres = conn.getresponse()
	edata = eres.read()
	ejsondata = json.loads(edata)['data']
	for d in ejsondata:
		event.attended[str(d['member']['id'])] = d['duration']
		if str(d['member']['id']) in people:
			people[str(d['member']['id'])].hrs +=  d['duration']
			people[str(d['member']['id'])].attended.append(event)
	events[event.id]= event

event_columns = [(event.name + " " + str(event.date)) for event in events.values()]
df = pd.DataFrame(columns=["Name"] + event_columns + ["Total Events Attended", "Total Duration"])

# Create an empty list to store DataFrames for each person
# Create an empty list to store DataFrames for each person
dfs = []

# Create a header row for event names and dates
header_row = ["Name"] + [col for col in df.columns if col != "Name"]

# Iterate through people
for person_id, person_instance in people.items():
    # Create a dictionary to store the data for this person
    person_data = {"Name": person_instance.name}
    
    # Initialize variables to calculate the total events attended and total duration
    total_events_attended = 0
    total_duration = 0
    
    # Iterate through events and populate the person's data
    for event_id, event_instance in events.items():
        if person_id in event_instance.attended:
            # If the person attended the event, record the duration
            duration = event_instance.attended[person_id]/60
            total_events_attended += 1
            total_duration += duration
        else:
            # If the person didn't attend the event, record 0 duration
            duration = 0
        
        # Parse the date string into a datetime object and then format it
        event_date = datetime.fromisoformat(event_instance.date[:-1])  # Remove 'Z' at the end
        formatted_date = event_date.strftime('%d/%m/%Y %H:%M')
        
        # Create a new column name with event name and formatted date
        event_column_name = f"{event_instance.name} {formatted_date}"
        
        # Add the event data to the person's dictionary with the new column name
        person_data[event_column_name] = duration
    
    # Add the total events attended and total duration to the person's dictionary
    person_data["Total Events Attended"] = total_events_attended
    person_data["Total Duration"] = total_duration
    
    # Append the person's data as a new DataFrame to the list
    dfs.append(pd.DataFrame([person_data]))

# Concatenate all DataFrames in the list into a single DataFrame
df = pd.concat(dfs, ignore_index=True)

# Define the path where you want to save the Excel file
excel_file_path = "attendance_data.xlsx"

# Export the DataFrame to an Excel file with header
with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, header=header_row)

print("DataFrame exported to Excel successfully.")