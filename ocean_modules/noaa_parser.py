#!/usr/bin/env python3 -tt

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin


class NoaaParser(object):
  '''This is an attempt to return useful data from the Noaa mobile marine weather pages. The NoaaParser Object is instantiated without attributes.'''
  def __init__(self):
    pass

  def parse_results(self, source):
    '''Take ndbc.noaa.gov page and return a dict of locations along with their full urls. This works on all the nav pages for ndbc.noaa.gov/mobile/?'''
    self.source = source
    self.loc_dict = {}
    with urlopen(self.source) as f:
      soup =  BeautifulSoup(f)  
    for link in soup.find_all('a'):
      self.loc_dict[link.string] = urljoin(self.source, link.get('href')) #builds dict out of locations and the urls to see those locations  
    self.clean_locs = {key : val for key, val in self.loc_dict.items() if "@" not in key} #this gets rid of mailto line and should leave only good values.
    return self.clean_locs

  def get_locations(self, search_key, result_dict):
    '''Given a search key and a dictionary of location/url results, the get_locations method will return urls specific to the search key.'''
    self.search_key = search_key
    self.result_dict = result_dict
    self.weather_sources = [val for key, val in self.result_dict.items() if self.search_key in key]
    if self.weather_sources:
      return self.weather_sources
    else:
      return "Search key not found"

  def weather_get(self, weather_sources):
    '''weather__get takes a list of urls and builds a dataset from those urls. This is the information retrieval method that simply dumps all data.'''
    self.weather_sources = weather_sources
    datalist = []
    for url in self.weather_sources:
      with urlopen(url) as f:
        weathersoup = BeautifulSoup(f)
        for node in weathersoup.find_all(['p', 'h2']):
          datalist.extend(node.find_all(text=True))
    # get rid of items containing the following:
    excludes = ["Feedback:", "Main", "webmaster.ndbc@noaa.gov"]
    results = [x.strip('\n') for x in datalist if not any(y in excludes for y in x.split())]  
    return [item for item in results if item]

  def weather_info_dict(self, weather_sources, time_zone):
    '''weather__info_dict takes a list of urls and builds a dictionary from those urls. This method drops some data that may be duplicated (for instance, where "Weather Summary" appears twice), but I prefer it because it produces cleaner, better organized information and still has the most important stuff.'''
    self.weather_sources = weather_sources
    self.time_zone = time_zone
    weather_dict = {}
    for url in self.weather_sources:
      with urlopen(url) as f:
        weathersoup = BeautifulSoup(f)
        for node in weathersoup.find_all('h2'):
          if node.string not in weather_dict.keys():
            if node.next_sibling == '\n':
              weather_dict[node.string] = node.next_sibling.next_sibling(text=True)
            # '.next_sibling.next_sibling' trick came directly from bs4 docs
            else:
              weather_dict[node.string] = node.next_sibling(text=True)

    # The following may be an abuse of the dictionary comprehension, 
    # but it was the easiest way to create a nested dictionary (for writing to csv)
    # It's not /that/ complex, though, once you realize it's mostly 
    # creating a new nested dictionary out of splitting up stuff on 
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
