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
    '''weather__get takes a list of urls and builds a dataset from those urls. This is the final information retrieval method.'''
    self.weather_sources = weather_sources
    self.datalist = []
    for url in self.weather_sources:
      with urlopen(url) as f:
        weathersoup = BeautifulSoup(f)
        for node in weathersoup.find_all(['p', 'h1', 'h2']):
          self.datalist.extend(node.find_all(text=True))
    # get rid of items containing the following:
    self.excludes = ["Feedback:", "Main", "webmaster.ndbc@noaa.gov"]
    self.results = [x.strip('\n') for x in self.datalist if not any(y in self.excludes for y in x.split())]  
    return [item for item in self.results if item]
