import requests, json
headers = {
'Authorization': 'Bearer XXX'
}

#Array of current first call members
FirstCall = []

minCallouts = {}

addToList = []
removeFromList []

##Get On-Call members
def getOnCall():
	memberurl = "https://api.d4h.org/v2/team/members?status=Operational"
	memberpayload={}
	memberresponse = requests.request("GET", memberurl, headers=headers, data=memberpayload).json()

	with open('members.json', 'w') as jsonFile:
		json.dump(memberresponse, jsonFile)

	with open("members.json", encoding='utf-8') as jsonFile:
	    jsonObject = json.load(jsonFile)
	    jsonFile.close()

	for d in jsonObject['data']:
		if d['status'] is not None and d['status']['label'] is not None and d['status']['label']['value'] is not None and d['status']['label']['value'] =='Útkall - (A útkall)' :
			FirstCall.append(d['id'])
	print(FirstCall)

def getCallouts():
	#Get Incident statistics from API

	incidenturl = "https://api.d4h.org/v2/team/attendance?activity=incident&after=2020-09-25&status=attending"
	incidentpayload={}
	incidentresponse = requests.request("GET", incidenturl, headers=headers, data=incidentpayload).json()
	print("incidentresponse")
	with open('callouts.json', 'w') as jsonFile:
		json.dump(incidentresponse, jsonFile)

	with open("callouts.json", encoding='utf-8') as jsonFile:
		jsonObject = json.load(jsonFile)
		jsonFile.close()

	for d in jsonObject['data']:
		if d['member']['id'] in minCallouts:
 			 minCallouts[d['member']['id']] += 1
		else:
  			minCallouts[d['member']['id']] = 1

def updateDetails():
	for  m in min callouts:
		if m in FirstCall:
			if 