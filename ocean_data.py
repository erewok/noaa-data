#!/usr/bin/python3 -tt

from ocean_modules.noaa_parser import NoaaParser
from ocean_modules.send_text import _tsend as send_text
import os

def read_config():
    data = {} 
    file = os.path.join(os.getcwd(), 'config', 'config')
    with open(file) as f:
        for line in f:
            if '=' in line:
                line = line.replace('"', '')
                data[line.rsplit(' = ')[0].strip()] = line.rsplit(' = ')[1].strip() 
                # I put spaces around the "=" because the url will have an "=" in it,
                # but the rest of the config data will have spaces around "=".
    return data

def ocean_data(source, my_loc):
    WeatherInfo = NoaaParser()
    all_locations = WeatherInfo.parse_results(source)
    my_sources = WeatherInfo.get_locations(my_loc, all_locations)
    return WeatherInfo.weather_get(my_sources)

if __name__=='__main__':
    configs = read_config()
    username = configs['EMAIL_USERNAME']    
    password = configs['EMAIL_PASSWORD']
    recipient = configs['RECIPIENT']
    region = configs['SET_REGION']
    location = configs['SET_LOCATION']
    message = '\n'.join(ocean_data(region, location))
    send_text(username, password, recipient, message)
