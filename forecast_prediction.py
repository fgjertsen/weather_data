#!/usr/bin/env python

""" Methods for obtaining weather data predictions from Met API ("LocationForecast")
    CREDENTIALS must be stored locally, by the user!
    
    Fredrik Gjertsen
"""

from datetime import datetime
from datetime import timedelta
import requests
import CREDENTIALS
import numpy as np
from matplotlib import pyplot as plt

class WeatherForecast:

    def __init__(self, Locations=['63.3945,10.4299']):
        self.api_endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/complete?'
        self.nLocations = len(Locations)
        self.locationCoordinates = []
        for i in range(self.nLocations):
            self.locationCoordinates.append({'locationNo': i, 'lat': Locations[i].split(",")[0], 'lon': Locations[i].split(",")[1]})
            self.locationNames = Locations
        
    
    # Function to fetch data from API
    def PullForecast(self):
    
        # Init. variable to store results
        locationData = []
        
        # Loop through locations
        for i in range(self.nLocations):
            # Set location specific string for query
            locationSpecificString = 'lat=' + self.locationCoordinates[i]['lat'] + '&lon=' + self.locationCoordinates[i]['lon']
            locationData.append({'time': [], 'air_temperature': [], 'air_pressure_at_sea_level': []})
            
            # Issue an HTTP GET request
            specific_endpoint = self.api_endpoint + locationSpecificString
            
            # Set header for query
            headers = {'User-Agent': CREDENTIALS.User_Agent(), 'From': CREDENTIALS.FromField()}
            r = requests.get(specific_endpoint, headers=headers)
            
            # Extract JSON data from response
            jsondata = r.json()
            timeseriesdata = jsondata['properties']['timeseries']
            
            # Loop through each point in time
            for j in range(len(timeseriesdata)):
                locationData[i]['time'].append(datetime.strptime(timeseriesdata[j]['time'], '%Y-%m-%dT%H:%M:%SZ'))
                instantData = timeseriesdata[j]['data']['instant']['details']
                locationData[i]['air_temperature'].append(instantData['air_temperature'])
                locationData[i]['air_pressure_at_sea_level'].append(instantData['air_pressure_at_sea_level'])
        
        return locationData


# Test call
if __name__ == '__main__':
    WF = WeatherForecast()
    res = WF.PullForecast()
    
    # Plot temperature predictions
    plt.figure
    for i in range(len(res)):
        time = res[i]['time']
        temp = res[i]['air_temperature']
        plt.plot(time, temp, label=WF.locationNames[i])
    plt.title('Air temperature, forecast')
    plt.legend(loc='best')
    plt.xlabel('Date/time [MM-DD HH]')
    plt.ylabel('Air temperature [' + u'\N{DEGREE SIGN}' + 'C]')
    plt.show()
    