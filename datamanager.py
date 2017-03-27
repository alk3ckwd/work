# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:41:33 2017

@author: mmcvicar
"""

import requests
from datetime import datetime, timedelta


url = 'https://app.wellcentive.com/DataManager/DataManager/j_spring_security_check'

payload = {'j_username': 'mmcvicar', 'j_password':'chachf5901'}
interfaces = {
'3958':'GE Centricity-HL7-CHA/CHF-PANW',
'3779':'GE Centricity-CCDA-CHA-PANW',
'3887':'EDIE-HL7-CHA/CHF',
'3956':'Aprima-CCDA-CHA/CHF-Olson Pediatric Clinic',
'4577':'Allscripts-HL7-CHA/CHF chaos',
'3955':'Aprima-CCDA-CHA/CHF-Sunset Pediatrics',
'4230':'EPIC-CCDA-CHA/CHF',
'3533':'Allscripts-CCDA-CHA-CHAoS',
'4713':'WVCH-AdvancedClaimsDelimited-CHA/CHF',
'4644':'WVCH-CHAWVCHealth Enrollment-CHA/CHF',
'4630':'Office Practicum-CCDA-CHA-OregonCityPeds',
'3498':'Other-GI-CHA',
'4640':'Daily Aetna-AetnaUniversalDelimited-CHA/CHF',
'4917':'PCC East Portland-CCDA-CHA/CHF',
'4629':'Office Practicum-CCDA-CHA-Gresham',
'3952':'Family Care-HL7 Med Claims-CHA/CHF',
'4645':'WVCH-CHAWVCHealth Enrollment Term-CHA/CHF',
'3778':'GI-GIAdvanced-CHA',
'4636':'Aetna-AetnaUniversalDelimited-CHA/CHF',
'3755':'Family Care-HL7-CHA/CHF',
'4747':'CHA-Greenway-Willamette Falls'
}
rundate = (datetime.today() - timedelta(days=1)).date().isoformat()
with requests.Session() as s:
    p = s.post('https://app.wellcentive.com/DataManager/DataManager/j_spring_security_check',data=payload)
    print('Results for ' + rundate)
    for k,v in interfaces.items():
        url = 'https://app.wellcentive.com/DataManager/page/support/manage.htm?pageAction=getDailyMessageProfile&interfaceId=' + k + '&start='+rundate+'&stop='+rundate+'&reference=false'
        #print('Results for ' + rundate)
        r = s.get(url)
        try:
            data = r.json()
            if data:
                processed = 0
                errored = 0
        
                for e in data['data']:
                    if e['ResultStatus'] == 'Error':
                        errored += e['Count']
                    else:
                        processed += e['Count']
                total = processed+errored
                if total > 0:
                    print(v + ': ' + str(errored+processed) + ' messages received. ' + str(errored/total) + '% error rate.')
                else:
                    print(v + ': No data recieved.')
        except:
            print(v + ': Failed to get data from DataManager.')
        
    s.close()