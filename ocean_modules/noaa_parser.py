#!/usr/bin/env python3 -tt

from collections import OrderedDict
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin


class NoaaParser(object):
  '''This is an attempt to return useful data from the Noaa mobile marine
weather pages. To use this, you have to instatiate a NoaaParser object
and then run .get_locations(search_key, source), where "source" is the
page of urls listing buoys in the region you want and "search_key" is
some location marker that shows up in the link or links that you want.
weather.get_location accepts only one search key at the moment, but
this will be changed in future iterations to retrieve multiple weather
reports.


  example usage:
  weather = NoaaParser()
  weather.get_locations("La Jolla", southwest_region_buoy_page)'''

  def __init__(self):
    self.weather_sources = []
    self.latitude = ''
    self.longitude = ''
    self.coords = []
    self.forecast_dict = {}

  def parse_results(self, source):
    '''Take ndbc.noaa.gov page and return a dict of locations along with their full urls.
    This works on all the nav pages for ndbc.noaa.gov/mobile/?'''

    self.source = source
    loc_dict = {}
    with urlopen(self.source) as f:
      soup =  BeautifulSoup(f)
      for link in soup.find_all('a'):
        if '@' in link.string:
          pass
        else:
          loc_dict[link.string] = urljoin(self.source, link.get('href')) #builds dict out of locations and the urls to see those locations
    return loc_dict

  def _set_coords(self, soup_obj):
    '''Takes final latitude and longitude listing from soup_obj instatiated by one of the get_weather functions and updates coordinates with the result.'''
    self.soup_obj = soup_obj
    self.coords = soup_obj.h1.next_sibling.string.split() # update latitude and longitude for use as class-level attribute
    self.latitude = self.coords[0][:-1] # Drops the "W" or "N" or whatever.
    self.longitude = self.coords[1][:-1]

  def get_locations(self, search_key, source):
    '''Given a search key and a url of result listings, the get_locations method will return urls specific to the search key.'''
    self.source = source
    self.search_key = search_key
    result_dict = self.parse_results(self.source)
    self.weather_sources = [val for key, val in result_dict.items() if self.search_key.lower() in key.lower()]
    if len(self.weather_sources) > 0:
      return self.weather_sources
    else:
      raise Exception("The location you entered was not found: try a different search key.\n Check the following source for valid search terms to find your location: \n{}".format(self.source))

  def weather_get_all(self):
    '''weather__get_all takes a list of urls and builds a dataset
    from those urls. This is the information retrieval method that simply dumps
    all data. You have to run get_locations(search_key, region_url)
    before this does anything because self.weather_sources must be populated.

    Usage: weather_get_all()
    returns: list of data from the previously selected location, and source url.'''

    datalist = []
    try:
      for url in self.weather_sources:
        with urlopen(url) as f:
          weathersoup = BeautifulSoup(f)
          for node in weathersoup.find_all(['p', 'h2']):
            datalist.extend(node.find_all(text=True))
    except NameError:
      raise Exception("weather_sources not defined")
    # get rid of items containing the following:
    excludes = ["Feedback:", "Main", "webmaster.ndbc@noaa.gov"]
    results = [x.strip('\n') for x in datalist if not any(y in excludes for y in x.split())]
    final_results = [item for item in results if item]

    if self.coords:
      return final_results
    else: #set class-level coordinates if unset.
      self.coords = [item for item in final_results[0].split()]
      self.latitude = self.coords[0][:-1] # Drops the "W" or "N" or whatever.
      self.longitude = self.coords[1][:-1]
      return final_results

  def weather_info_dict(self, time_zone):
    '''weather__info_dict takes a time-zone and builds a dictionary from
already-generated buoy urls. This method drops some data that may be duplicated
(for instance, where "Weather Summary" appears twice), but I prefer it because
it produces cleaner, better organized information and still has the most
important stuff. You have to run get_locations(search_key, region_url)
before this does anything because self.weather_sources must be populated.

    usage: weather_info_dict(time-zone-for-desired-results)

    Returns: nested dictionary that looks like "{'Weather Summary' {'time': '8:05'}, 'Wave Summary' : {'etc.'}}'''
    self.time_zone = time_zone
    weather_dict = {}
    try:
      for url in self.weather_sources:
        with urlopen(url) as f:
          weathersoup = BeautifulSoup(f)
          if self.coords:
            pass
          else: #set class-level coordinates if unset.
            self._set_coords(weathersoup)
          for node in weathersoup.find_all('h2'):
            if node.string not in weather_dict.keys():
              if node.next_sibling == '\n':
                weather_dict[node.string] = node.next_sibling.next_sibling(text=True)
                # 'the .next_sibling.next_sibling' trick came directly from bs4 docs
              else:
                weather_dict[node.string] = node.next_sibling(text=True)
    except NameError:
        raise Exception("weather_sources not defined")
    # The following creates a new nested dictionary out of splitting up stuff on
    # either side of the colon. Thus, {"Weather : ["Air Temp: 66.0", etc.] becomes:
    # {"Weather : {"Air Temp" : "66.0"}} etc.

    data_final = {key : {val.rsplit(":")[0].strip() : val.rsplit(":")[1].strip() for val in value if val.strip() and "GMT" not in val and self.time_zone not in val} for key, value in weather_dict.items()}

    # Last run through makes sure there's a 'Time' key in the dict. It was
    # hard to get with that colon in it before!
    if "Time" not in data_final.keys():
      for list_of_info in weather_dict.values():
        for _item in list_of_info:
          if self.time_zone in _item:
            data_final["Time"] = _item.strip()
    return data_final

  def get_forecast(self):
    '''Takes the latitude and longitude and uses forecast url to retrieve
the forecast for that location. Conjecture seems to be that: marine-buoy lat
and lon correspond to marine weather forecasts, while terrestrial lat and lon
correspond to terrestrial weather reports. Test further to confirm.

    usage: get_forecast().

    returns: True or False. Use prettify forecast to get results or get it from the class attribute directly: self.forecast_dict. '''
    if not self.coords: # Class-level coordinates are needed to get forecast page
      if not self.weather_sources:
        raise Exception("You will have to selet a weather page before getting the forecast. Try this first: get_locations('search key', 'region-url')\n\n")
      else:
        url = self.weather_sources[0]
        with urlopen(url) as f:
          forecastsoup = BeautifulSoup(f)
          self._set_coords(forecastsoup)

    forecast_url = "http://forecast.weather.gov/MapClick.php?lat={self.latitude}&lon=-{self.longitude}&unit=0&lg=english&FcstType=digital"
    self.forecast_page = forecast_url.format_map(vars())

    ##IMPORTANT: Long is set to negative on the west coast of the USA,
    # check full forecast url for details elsewhere and to see if your
    # lat or long are negative inside the url.
    # Adjust forecast_page accordingly if so.

    with urlopen(self.forecast_page) as f:
      forecastsoup = BeautifulSoup(f)
# ---------------------------------GET FIELD NAMES -----------------#
      field_names = []
    ### ---- Get "Hour" --- ###
      for node in forecastsoup.find_all(attrs={'align':'left', 'class':'date'}):
        if node.string not in field_names:
          field_names.append(node.string)

    ### ---- Get Other Fields in first column --- ###
      for node in forecastsoup.find_all(attrs={'align':'left', 'width':'5%'}):
        if node.string not in field_names and node.string != "Date":
          field_names.append(node.string)

    ### ---- Get all the hours listed  ---### Times have no other attributes: that's the pattern
      first_row_times = []
      for node in forecastsoup.find_all(attrs={'class' : 'date', 'align': None, 'width': None}):
        if node.string not in first_row_times:
          first_row_times.append(node.string)

    # Lastly, we want 24-hours worth of data multiplied by 11 rows.
    # first_fields is 11 field_names plus hour, but the "hours" have
    # already been pulled out as our first-row header. Thus, we need to subtract the "hour" row.
    # We do this by subtracting one from the field names to get the remaining total cells to pull from.
    # This is the logic for the limit below.
      table_width = len(first_row_times)
      cell_data = []
      for node in forecastsoup.find_all(attrs={'align' : 'center', 'width' : '3%'}, limit = table_width * (len(field_names) -1)):
        cell_data.append(node.string)

      for x in range(len(field_names)-1):
        self.forecast_dict[field_names[x + 1].strip()] = (OrderedDict(zip(first_row_times, cell_data[table_width*x:table_width*(x+1)])))

    if self.forecast_dict:
      return True
    else:
      return False

  def prettify_forecast(self, hours_ahead=6):
    """prettify_forecase takes the forecast generated by get_forecast() and yields it in a pretty format.

    It's actually a generator for use in message or email creation or for web display.

    prettify_forecast() takes an optional argument 'hours_ahead=n' where 'n' is the number of hours ahead you would like to forecast (max 24)."""

    if not self.forecast_dict:
      self.get_forecast()
    else:
      pass
    self.hours_ahead = hours_ahead

    for key in self.forecast_dict.keys():
      for item in list(self.forecast_dict[key].keys())[:self.hours_ahead]:
        if self.forecast_dict[key][item] != None:
          yield key.strip(), item + "h:", self.forecast_dict[key][item]
        else:
          pass
