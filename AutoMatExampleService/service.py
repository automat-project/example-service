# AutoMat SDK Example Service
import datetime
import json
import random

import numpy as np
import requests
from flask import Flask, render_template, request

CONFIG_IP = "0.0.0.0"
CONFIG_PORT = 5000
CONFIG_APIKEY = "<INPUT_APIKEY_HERE>"
CONFIG_APIURL = "<INPUT_MARKETPLACE_URL_HERE>"
CONFIG_OFFERID = "<INPUT_OFFER_ID_HERE>"
CONFIG_OFFERSUBSCRIPTION = "<INPUT_OFFER_SUBSCRIPTION_URL_HERE>"

## Main Application
# Start/Landingpage
app = Flask(__name__)
app.debug = False

@app.route("/")
def startpage():
    return render_template('home.html')

# Pull approach
@app.route("/pull_map")
def pull_map():
    ''' retrieves the latest CVIM position data packages '''
    url = CONFIG_APIURL + "/ServiceProviderOffer/" + CONFIG_OFFERID + "/cvimDataPackages"
    params = {
        "sort": "submit-time",
        "order": "desc",
        "limit": 10,
        "where": json.dumps({"channels": ["2"]}, separators=(',', ':'))
    }
    headers = {
        "X-Auth-Token": CONFIG_APIKEY
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        cvim_js = "var cvim=%s;" % response.content.decode()
        return render_template('pull_map.html', cvim=cvim_js)
    else:
        return render_template('pull_map.html', cvim=[])

# Pull trips
@app.route("/pull_trips")
def pull_trips():
    # get trips
    url = CONFIG_APIURL + "/ServiceProviderOffer/5a3a672f6abe501c00dacdf2/"
    headers = {
        "X-Auth-Token": CONFIG_APIKEY
    }
    print("Downloading trip data")
    response = requests.get(url + "trips", headers=headers)

    jsdata = []
    if response.status_code == 200:
        try:
            # download cvim data for each trip
            for trip in json.loads(response.content.decode()):
                if trip["datapackage-count"] < 2:
                    continue
                # retrieve cvimdata
                print("Evaluating trip ", trip["trip-id"], "and receive CVIM data")
                resp_trip = requests.get(url + "cvimDataPackages", headers=headers, params={
                    "where": json.dumps({"trip-id": trip["trip-id"]}, separators=(',', ':'))
                })

                ## process cvim data
                # find position and speed data
                position_data = None
                speed_data = None
                for data_package in json.loads(resp_trip.content.decode()):
                    # speed data package (MCID==1)
                    if data_package["measurement-channel-id"] == "1":
                        speed_data = data_package["data"]
                    # position data package (MCID==2)
                    elif data_package["measurement-channel-id"] == "2":
                        position_data = data_package["data"]

                # Align time: interpolate speed data
                if position_data and speed_data:
                    t_position = [datetime.datetime.strptime(x['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() for x in position_data]
                    t_speed    = [datetime.datetime.strptime(x['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() for x in speed_data]
                    data_speed = [x["value"] for x in speed_data]
                    
                    data_interp = list(np.interp(t_position, t_speed, data_speed))
                    trip = []
                    for i, position in enumerate(position_data):
                        trip.append([position["value"][0], position["value"][1], data_interp[i]])
                    jsdata.append(trip)
        except Exception as ex:
            print("An error occured: ", str(ex))
    return render_template('pull_trips.html', tripdata="var tripdata=%s;" % json.dumps(jsdata))

# Push/Live Data Retrieval
@app.route("/push")
def push():
    return render_template('push.html', id="sdk%d" % random.randint(0,10), url=CONFIG_OFFERSUBSCRIPTION)

# Start app
app.run(host=CONFIG_IP, port=CONFIG_PORT)
