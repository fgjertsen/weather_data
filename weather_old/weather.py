# -*- coding: utf-8 -*-
#
#   Using deprecated yr.no API: Consider porting to Frost/LocationForecast
#       (yr.no API will be discontinued after Feb2022!)
#
#   Author: Fredrik Gjertsen <fredrik.gjertsen@gmail.com>
#   Declaration: Software as is. No warranty.
#
#   Credit: «Data from The Norwegian Meteorological Institute»
#   License: Data and products are licensed under Norwegian license for public data (NLOD - https://data.norge.no/nlod/en/2.0/)
#     and Creative Commons 4.0 BY International (https://creativecommons.org/licenses/by/4.0/)
#
#   Python ver. 3.9

def get_weather_prediction(region='Tr%C3%B8ndelag', county='Trondheim', city='Trondheim'):

    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen
    from datetime import datetime
    import xml.etree.ElementTree as ET
    
    # Connect to API and declare tables
    url_short = 'http://www.yr.no/place/Norge/' + region + '/' + county + '/' + city + '/forecast_hour_by_hour.xml'   # Hour-by-hour forecast (short term)
    url_longt = 'http://www.yr.no/place/Norge/' + region + '/' + county + '/' + city + '/forecast.xml'                # Long-term forecast
    root_short = ET.parse(urlopen(url_short)).getroot()
    root_longt = ET.parse(urlopen(url_longt)).getroot()
    
    forecast_short = root_short.find('forecast')
    forecast_longt = root_longt.find('forecast')
    tabular_short = forecast_short.find('tabular')
    tabular_longt = forecast_longt.find('tabular')
    place = forecast_short.find('text').find('location').get('name')
    
    # List each datapoint in time, both short-term and long-term
    times_short = tabular_short.findall('time')
    times_longt = tabular_longt.findall('time')
    
    # Find point to merge forecasts
    last_time_short = datetime.strptime(times_short[-1].get('to'), '%Y-%m-%dT%H:%M:%S')
    i = 0
    for current_time in times_longt:
        to_time =  datetime.strptime(current_time.get('to'), '%Y-%m-%dT%H:%M:%S')
        if to_time > last_time_short:
            break
        i += 1
    
    # Augment vector of data points in time
    times = times_short + times_longt[i:]
    start_time = datetime.strptime(times[0].get('from'), '%Y-%m-%dT%H:%M:%S')
    
    # Prepare vectors
    t = []      # Time          [hours]
    T = []      # Temperature   [deg. C]
    p = []      # Pressure      [hPa]
    tfr = []    # From-times    [datetime]
    tto = []    # To-times      [datetime]
    
    # Organize data
    j = 0
    for current_time in times:
        
        if j == len(times_short):
            from_time = last_time_short
        else:
            from_time = datetime.strptime(current_time.get('from'), '%Y-%m-%dT%H:%M:%S')
        to_time =  datetime.strptime(current_time.get('to'), '%Y-%m-%dT%H:%M:%S')
        temperature = current_time.find('temperature').get('value')
        pressure = current_time.find('pressure').get('value')
            
        start = from_time-start_time
        end = to_time-start_time
        
        t.append(start.days *24.0 + start.seconds /3600.0)
        T.append(float(temperature))
        p.append(float(pressure))
        tfr.append(from_time)
        tto.append(to_time)
        
        j += 1
    
    # Return data of interest
    return t, T, p, tfr, tto


if __name__ == "__main__":

    place = 'Trondheim'
    t, T, p, tfr, tto = get_weather_prediction(city=place)
    
    # Print table of information to console
    print("\n============== " + place + " weather forecast ===============================")
    print("From\t\t\tTo\t\t\tTemp.\t\tPress.")
    print("yyyy-mm-dd hh:mm:ss\tyyyy-mm-dd hh:mm:ss\t[deg. C]\t[hPa]")
    print("-------------------------------------------------------------------------")
    for i in range(0, len(t)):
        print(str(tfr[i]) + "\t" + str(tto[i]) + "\t " + '{:+}'.format(int(T[i])) + "\t\t " + str(float(p[i])))
    print("-------------------------------------------------------------------------")
    
    # Make plots
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle('Weather forecast, ' + place)
    # Temperature curve
    axs[0].step(t, T, where='post')
    axs[0].set_title('Temperature')
    axs[0].set(xlabel='Time [hours]', ylabel='Temperature [deg. C]')
    axs[0].label_outer()
    axs[0].autoscale(enable=True, axis='x', tight=True)
    # Pressure curve
    axs[1].step(t, p, where='post')
    axs[1].set_title('Pressure')
    axs[1].set(xlabel='Time [hours]', ylabel='Pressure [hPa]')
    axs[1].autoscale(enable=True, axis='x', tight=True)
    plt.show()