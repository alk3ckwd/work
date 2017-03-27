import requests
from datetime import datetime
import sqlite3
import time
from twilio.rest import TwilioRestClient

headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
           'origin':'https://fastpokemap.se',
           'authority':'api.fastpokemap.se'}

headers2 = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
           'origin':'https://fastpokemap.se',
           'authority':'cache.fastpokemap.se'}

locations = [{'lat':'45.47961017943774','lng':'-122.67343640327455'},
             {'lat':'45.48128770839176','lng':'-122.67340421676637'}]


poke_alerts = ["DRATINI", "DRAGONAIR", "DRAGONITE", "SNORLAX", "ARCANINE", "GROWLITHE", "CHARMANDER"]


def textAlert(message):
    accountSID = "ACa3c86d8cd502dad3e0b1272506363e08"
    authToken = "b80517455608728fcc92625925fe527e"
    myNumber = "+15417604302"
    twilioNumber = "+15412309206"
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)

def log_spawn(spawn,data_type):
    conn = sqlite3.connect('spawns2.sqlite')
    c = conn.cursor()

    c.execute("SELECT * FROM locations WHERE enc_id={enc_id}".format(enc_id=spawn[0]))
    id_exists = c.fetchone()

    if id_exists:
        print(spawn[1] + " spawn already logged")
    else:
        print("Logging " + spawn[1] + " spawn")
        spawn.append(str(datetime.now()))
        c.execute("INSERT INTO locations values (?,?,?,?,?,?);",spawn)
        conn.commit()
        print("Log successful")
        if spawn[1] in poke_alerts and data_type == 'normal' and datetime.now().hour >= 8 and datetime.now().hour <= 15 and datetime.now().weekday < 5:
            textAlert("A " + spawn[1] + " has been found nearby!")
    conn.close()


def parse(data,data_type):
    print("Parsing " + data_type + " spawns")
    if data_type == 'normal':
        for spawn in data['result']:
            if 'lure_info' in spawn:
                pass
            else:
                for key, value in spawn.items():
                    if key=='pokemon_id':
                        pid=value
                    elif key=='latitude':
                        lat=value
                    elif key=='longitude':
                        lng=value
                    elif key=='spawn_point_id':
                        spawn_id=value
                    elif key=='encounter_id':
                        enc_id=value
                log_spawn([enc_id, pid, lat, lng, spawn_id],data_type)
    else:
        for spawn in data:
            if 'lure_info' in spawn:
                pass
            else:
                for key, value in spawn.items():
                    if key=='pokemon_id':
                        pid=value
                    elif key=='spawn_id':
                        spawn_id=value
                    elif key=='encounter_id':
                        enc_id=value
                    elif key=='lnglat':
                        lat = value['coordinates'][1]
                        lng = value['coordinates'][0]
                log_spawn([enc_id, pid, lat, lng, spawn_id],data_type)


def scan(lat, lng):
    result = False
    print("Scanning...")
    while not result:
        r = requests.get('https://api.fastpokemap.se/?key=allow-all&ts=0&lat=' + lat + '&lng=' + lng, headers=headers)
        try:
            data = r.json()
            try:
                print(data['error'])
                time.sleep(2)
            except:
                print("Got valid result")
                print(data)
                break
        except:
            print("Bad response")
            time.sleep(2)
    return data

while True:
    
    for location in locations:
        spawns = scan(location['lat'],location['lng'])
        parse(spawns,'normal')
        time.sleep(90)
    cached = requests.get('https://cache.fastpokemap.se/?key=allow-all&ts=0&compute=104.131.176.26&lat=45.58378533518524&lng=-122.69481897354127', headers=headers2).json()
    parse(cached,'cache')
    time.sleep(5)
