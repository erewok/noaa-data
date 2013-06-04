#!/usr/bin/env python3 -tt

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin


class NoaaParser(object):
  '''This is an attempt to return useful data from the Noaa mobile marine weather pages. To use this, you have to instatiate a NoaaParser object and then run .get_locations(search_key, source).'''
  def __init__(self):
    self.weather_sources = []
    self.latitude = ''
    self.longitude = ''
    self.coords = []

  def parse_results(self, source):
    '''Take ndbc.noaa.gov page and return a dict of locations along with their full urls. This works on all the nav pages for ndbc.noaa.gov/mobile/?'''
    self.source = source
    loc_dict = {}
    with urlopen(self.source) as f:
      soup =  BeautifulSoup(f)  
      for link in soup.find_all('a'):
        loc_dict[link.string] = urljoin(self.source, link.get('href')) #builds dict out of locations and the urls to see those locations  
    clean_locs = {key : val for key, val in loc_dict.items() if "@" not in key} #this gets rid of mailto line and should leave only good values.
    return clean_locs

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
    self.weather_sources = [val for key, val in result_dict.items() if self.search_key in key]
    if len(self.weather_sources) > 0:
      return self.weather_sources
    else:
      raise Exception("The location you entered was not found: try a different search key.")

  def weather_get_all(self):
    '''weather__get takes a list of urls and builds a dataset from those urls. This is the information retrieval method that simply dumps all data.
    Usage: weather_get_all()'''
    datalist = []
    for url in self.weather_sources:
      with urlopen(url) as f:
        weathersoup = BeautifulSoup(f)
        for node in weathersoup.find_all(['p', 'h2']):
          datalist.extend(node.find_all(text=True))
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
    '''weather__info_dict takes a list of urls and builds a dictionary from those urls. This method drops some data that may be duplicated (for instance, where "Weather Summary" appears twice), but I prefer it because it produces cleaner, better organized information and still has the most important stuff.
    usage: weather_info_dict(list-of-weather-urls, time-zone-for-those-results)
    Returns: nested dictionary that looks like "{'Weather Summary' {'time': '8:05'}}
    '''
    self.time_zone = time_zone
    weather_dict = {}
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

    # The following may be an abuse of the dictionary comprehension, 
    # but it was the easiest way to create a nested dictionary (for writing to csv)
    # It creates a new nested dictionary out of splitting up stuff on 
    # either side of the colon. Thus, {"Weather : ["Air Temp: 66.0", etc.] becomes:
    # {"Weather : {"Air Temp" : "66.0"}} etc.

    data_final = {key : {val.rsplit(":")[0].strip() : val.rsplit(":")[1].strip() for val in value if val.strip() and "GMT" not in val and self.time_zone not in val} for key, value in weather_dict.items()} # 'if val.strip()' checks to make sure it's not empty once whitespace is gone.

    # Last run through makes sure there's a 'Time' key in the dict. It was
    # hard to get with that colon in it before! 
    if "Time" not in data_final.keys():
      for list_of_info in weather_dict.values():
        for _item in list_of_info:
          if self.time_zone in _item:
            data_final["Time"] = _item.strip()
    return data_final

  def get_forecast(self):
    '''Takes the latitude and longitude and uses forecast url to retrieve the forecast.'''
    if not self.coords: # Class-level coordinates are needed to get forecast page
      if not self.weather_sources:
        raise Exception("You will have to selet a weather page before getting the forecast. Try some of the other methods first.")
      else:
        url = self.weather_sources[0]
        with urlopen(url) as f:
          weathersoup = BeautifulSoup(f)
          self._set_coords(weathersoup)

    forecast_page = "http://forecast.weather.gov/MapClick.php?lat={}&lon=-{}&unit=0&lg=english&FcstType=digital".format(self.latitude, self.longitude)
    ##IMPORTANT: Long is set to negative on the west coast of the USA, check full forecast url for details elsewhere and to see if your lat or long are negative inside the url. 
    with urlopen(forecast_page) as f:
      forecastsoup = BeautifulSoup(f)
      print(forecastsoup.prettify())

