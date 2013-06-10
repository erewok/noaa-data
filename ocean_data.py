#!/usr/bin/python3 -tt

import os

from configparser import ConfigParser, ExtendedInterpolation

from ocean_modules.noaa_parser import NoaaParser
from ocean_modules.send_text import _tsend as send_text

class NoaaData(object):
    
    def __init__(self, location, source):
        self.weather = NoaaParser()
        self.source = source
        self.location = location

    def ocean_data_all(self):
        '''This function retrieves all available data for location listed.'''
        self.weather.get_locations(self.location, self.source)
        return self.weather.weather_get_all()

    def ocean_data_clean(self, time_zone):
        '''This function returns a cleaner version, a bit stripped-down.'''
        self.time_zone = time_zone
        self.weather.get_locations(self.location, self.source)
        return self.weather.weather_info_dict(self.time_zone)

    def get_forecast(self, **hours):
        '''This will return a forecast generator that defaults to six-hours in advance, but which can return up to 24 hours of data.'''
        if not self.location or not self.source:
            self.weather.get_locations(self.location, self.source)
        else:
            pass
        self.hours = hours
        if len(self.hours) == 1:
            for k, v in self.hours.items():
                return self.weather.prettify_forecast(hours_ahead=v)
        else:
            return self.weather.prettify_forecast()

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

# def receive_requests(username, password, server):
    # Ideally, this will be the part that watches for changes...
    # It will go somewhere else...
#    new_mails = check_mail.receive_email(username, password, server)
#    senders_requests = check_mail.email_parsing_from_SMS(new_mails)
#    return senders_requests


def read_config():
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    script_dir = os.path.dirname(os.path.realpath(__file__))
    conf_file = os.path.join(script_dir, 'config', 'config')
    parser.read(conf_file)
    return parser

if __name__=='__main__':
    configs = read_config()
    # Email configs: server allows checking of address if set-up
    email_server = configs['email']['server']
    username = configs['email']['username']
    password = configs['email']['password']

    recipient = configs['cell settings']['recipient']
    
    # Location settings
    source = configs['noaa.gov settings']['my_source']
    location = configs['noaa.gov settings']['location']
    time_zone = configs['location settings']['set_time_zone']
    all_dat = configs['forecast settings'].getboolean('send_all_data')
    forecast = configs['forecast settings'].getboolean('send_marine_forecast')
    hours_ahead = configs['forecast settings']['hours_ahead_to_forecast']

    weather_obj = NoaaData(location, source)

#    if all_dat:
#      message = weather_obj.ocean_data_all() # returns a list
#    else:
#      message = weather_obj.ocean_data_clean(time_zone) # returns a dict

#    print(message)
    print(weather_obj.ocean_data_all())
    if forecast:
        for n in weather_obj.get_forecast(hours=hours_ahead):
            print(n)
    else:
        pass

#    weather_msg = location + '\n' + str(make_message(message) # has problems with unicode

#    send_text(username, password, recipient, weather_msg)
