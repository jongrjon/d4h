import http.client
import json
from datetime import datetime, timedelta

TOKEN = input("API TOKEN: ")
MIN_HRS = int(input("Mininum Hrs worked: "))-1
MIN_INC = int(input("Minimum nr. of callouts "))-1

startdate = (datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d")
print(startdate)
status =["Operational","Non-Operational"]
conn = http.client.HTTPSConnection("api.d4h.org")
payload = ''
headers = {
  'Authorization': 'Bearer '+TOKEN
}
users = []

class Person:
    def __init__(self,ref, name, uid):
        self.ref = ref
        self.name = name
        self.id = uid
        self.hrs = 0
        self.incidents = 0

    def __repr__(self):
        return str(self.ref)+" "+str(self.name)+" "+str(round(self.hrs, 2))+" "+str(self.incidents)

for s in status:
    conn.request("GET", "/v2/team/members?status="+s, payload, headers)
    res = conn.getresponse()
    data = res.read()
    jasondata = json.loads(data)
    for d in jasondata["data"]:
        if d['ref'].find("G")==d['ref'].find("N")==d['ref'].find("U")==-1:
            uid = str(d["id"])
            conn.request("GET","/v2/team/attendance?status=attending&member="+uid+"&after="+startdate, payload, headers)
            user_res = conn.getresponse()
            user_data = user_res.read()
            user_jason = json.loads(user_data)
            user = Person(d['ref'], d['name'], d['id'])
            for u in user_jason["data"]:
                if u["activity"]["type"] == "incident":
                    user.incidents += 1
                user.hrs += u["duration"]/60
            if user.hrs >MIN_HRS or user.incidents > MIN_INC:
                users.append(user)

users.sort(key=lambda u: u.name)
for u in users:
    print(u)
