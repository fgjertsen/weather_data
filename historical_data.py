#!/usr/bin/env python

""" Methods for obtaining historical weather data from Met API ("Frost")
    CREDENTIALS must be stored locally, by the user!
    
    Fredrik Gjertsen
"""

from datetime import datetime
from datetime import timedelta
import requests
import CREDENTIALS
import numpy as np
from matplotlib import pyplot as plt

class WeatherHistory:
    
    # Class constructor
    # SN68230 = Risvollan målestasjon
    # SN68863 = Voll PLU målestasjon
    def __init__(self, Locations='SN68230,SN68863'):
        self.client_id = CREDENTIALS.Frost_ClientID()
        self.api_endpoint = 'https://frost.met.no/observations/v0.jsonld'
        
        # Parameters for API calls
        self.Locations = Locations
        self.nLocations = Locations.count(",") + 1
        self.Variables = 'air_temperature,air_pressure_at_sea_level'
        
    
    # Function to fetch data from API
    def PullHistoricalData(self, start_date='three_days_ago', start_time='00:00', end_date='today', end_time='now'):
    
        # Init. error code
        nErr = 0
        ErrorMessage = 'OK!'
        
        # Treat input arguments, if necessary
        if end_date == 'today':
            end_date = datetime.strftime( datetime.today(), '%Y-%m-%d' )
        if end_time == 'now':
            end_time = datetime.strftime( datetime.now(), '%H:%M' )
        if start_date == 'three_days_ago':
            start_date = datetime.strftime( (datetime.today() - timedelta(days=3)), '%Y-%m-%d' )
        
        # Define parameters for the data request
        timeInterval = start_date + 'T' + start_time + '/' + end_date + 'T' + end_time
        parameters = {
            'sources': self.Locations,
            'elements': self.Variables,
            'referencetime': timeInterval,
        }
        
        # Issue an HTTP GET request
        r = requests.get(self.api_endpoint, parameters, auth=(self.client_id,''))
        
        # Extract JSON data from response
        jsondata = r.json()
        if r.status_code == 200:
            pass
        else:
            nErr = r.status_code
            JSONErrorMessage = ('Message: %s' % jsondata['error']['message'])
            JSONErrorReason = ('Reason: %s' % jsondata['error']['reason'])
            ErrorMessage = JSONErrorMessage + ', ' + JSONErrorReason
            return
        
        # Dissect JSON data
        data = jsondata['data']
        
        # Start sorting data
        LocationList = self.Locations.split(",")
        outData = {};
        for i in range(self.nLocations):
            outData[LocationList[i]] = {'sourceId': LocationList[i], 'time': [], 'air_temperature': [],  'air_pressure_at_sea_level': []}
        for i in range(len(data)):
            # Sort observation by station
            sourceId = data[i]['sourceId'].split(":")[0]
            time = datetime.strptime(data[i]['referenceTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
            outData[sourceId]['time'].append(time)
            # Loop through observations
            print(data[i])
            observations = data[i]['observations']
            for j in range(len(observations)):
                # Save air temperatures
                if (observations[j].get('elementId') == 'air_temperature'):
                    outData[sourceId]['air_temperature'].append(observations[j].get('value'))
                # Save air pressures
                if (observations[j].get('elementId') == 'air_pressure_at_sea_level'):
                    outData[sourceId]['air_pressure_at_sea_level'].append(observations[j].get('value'))
        
        return {'nErr': nErr, 'ErrorMessage': ErrorMessage, 'Data': outData}


# Test call
if __name__ == '__main__':
    WH = WeatherHistory()
    res = WH.PullHistoricalData()
    if res['nErr'] != 0:
        print('Error code' + res['nErr'] + 'from function!')
        quit()
    
    data = res['Data'];
    
    # Plot temperature history
    plt.figure
    for station in data.keys():
        time = data[station]['time']
        temp = data[station]['air_temperature']
        plt.plot(time, temp, label=data[station]['sourceId'])
    plt.title('Air temperature, historical data')
    plt.legend(loc='best')
    plt.xlabel('Date/time [MM-DD HH]')
    plt.ylabel('Air temperature [' + u'\N{DEGREE SIGN}' + 'C]')
    plt.show()