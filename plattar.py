import http.client
import json
import math
from datetime import datetime, timedelta

TOKEN = input("API TOKEN: ")

startdate = datetime(1999,9,1).strftime("%Y-%m-%d")
print(startdate)
status =["Operational","Non-Operational"]
conn = http.client.HTTPSConnection("api.d4h.org")
payload = ''
headers = {
  'Authorization': 'Bearer '+TOKEN
}

highest = 0
users = []
milestones = []
class Person:
    def __init__(self,ref, name, uid):
        self.ref = ref
        self.name = name
        self.id = uid
        self.incidents = 0
        self.milestones =[]

    def __repr__(self):
        return str(self.ref)+", "+str(self.name)+", "+str(self.incidents)

for s in status:
    conn.request("GET", "/v2/team/members?status="+s, payload, headers)
    res = conn.getresponse()
    data = res.read()
    jasondata = json.loads(data)
    for d in jasondata["data"]:
        if d['ref'].find("G")==d['ref'].find("N")==d['ref'].find("U")==-1:
            uid = str(d["id"])
            conn.request("GET","/v2/team/attendance?status=attending&activity=incident&member="+uid+"&after="+startdate+"&limit=751", payload, headers)
            user_res = conn.getresponse()
            user_data = user_res.read()
            user_jason = json.loads(user_data)
            user = Person(d['ref'], d['name'], d['id'])
            user.incidents = len(user_jason["data"])
            if user.incidents > highest:
                highest = user.incidents
                while len(milestones) < math.floor(highest/100):
                    milestones.append([])
            user_jason["data"].sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%S.%fZ'))
            user.milestones = user_jason["data"][99::100]
            for i in range(0,len(user.milestones)):
                milestones[i].append({user:user.milestones[i]["date"][0:10]})

            users.append(user)
for m in milestones:
    m.sort(key=lambda x: datetime.strptime(x[list(x.keys())[0]], '%Y-%m-%d'))

print(highest)
for i in range(1, math.floor(highest/100)+1):
    print(str(i*100)+" UTKOLL:"+str(len(milestones[i-1]))+" Felagar")
    for m in milestones[i-1]:
        print(str(list(m.keys())[0])+" "+m[list(m.keys())[0]])
    """ for u in users:
        if u.incidents/100 >= i:
            print(str(u)+" "+u.milestones[i-1]["date"]) """

