#!/usr/bin/python3 -tt

from ocean_modules.noaa_parser import NoaaParser
from ocean_modules.send_text import _tsend as send_text
from configparser import ConfigParser, ExtendedInterpolation
import os

def read_config():
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    script_dir = os.path.dirname(os.path.realpath(__file__))
    conf_file = os.path.join(script_dir, 'config', 'config')
    parser.read(conf_file)
    return parser

def ocean_data_all(source, my_loc):
    '''This function retrieves all available data for "my_loc".'''
    WeatherInfo = NoaaParser()
    my_sources = WeatherInfo.get_locations(my_loc, source)
    return WeatherInfo.weather_get_all()

def ocean_data_clean(source, my_loc, time_zone):
    '''This function returns a cleaner version, a bit stripped-down.'''
    WeatherInfo = NoaaParser()
    my_sources = WeatherInfo.get_locations(my_loc, source)
    return WeatherInfo.weather_info_dict(time_zone)

#def marine_forecast(source, my_loc):
#    WeatherInfo = NoaaParser()
#    my_sources = WeatherInfo.get_locations(my_loc, source)
#    return 

def make_message(input_data):
    '''Returns a string from input_data after testing whether input is list
    or dict. Dict will actually be a nested dict (see noaa_parser.py)'''
    messagestring = ''
    if isinstance(input_data, list):
        messagestring = '\n'.join(input_data)
    elif isinstance(input_data, dict):
        for key, val in input_data.items():
            messagestring += key + '\n'
            if isinstance(val, dict):
                for newkey, newval in val.items():
                    messagestring += newkey + ' ' + newval + '\n'
            else:
                messagestring += val + '\n'
    return messagestring
        

if __name__=='__main__':
    configs = read_config()
    username = configs['email']['username']    
    password = configs['email']['password']
    recipient = configs['cell settings']['recipient']
    region = configs['noaa.gov settings']['region']
    location = configs['noaa.gov settings']['location']
    time_zone = configs['location settings']['set_time_zone']
    all_dat = configs['data requested'].getboolean('send_all')
    if all_dat:
      message = ocean_data_all(region, location) # returns a list
    else:
      message = ocean_data_clean(region, location, time_zone) # returns a dict

    weather_msg = location + '\n' + make_message(message)

#    send_text(username, password, recipient, weather_msg)
