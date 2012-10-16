from classes import *
from util import *

import httplib, json

apikey = '6117a56225f311c3'

name = 'weather underground'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('WEATHER', 0, weather, 1, helpweather, reqchan=False)
	cache.hookcmd('W', 0, weather, 1, helpw, reqchan=False)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('WEATHER')
	cache.unhookcmd('W')

def weather(nick, target, params, bot, cache):
	location = params.strip().replace(' ', '_')
	conn = httplib.HTTPConnection("api.wunderground.com")
	conn.request("GET", "/api/%s/conditions/q/%s.json" % (apikey, location))
	res = conn.getresponse()
	if res.status == 200:
		data = res.read()
		wz = json.loads(data)
		if 'current_observation' in wz:
			wz = wz['current_observation']
			buf = "Weather for %s, %s: %s - Feels like: %s - Conditions: %s - Humidity: %s. %s" % (wz['display_location']['full'], wz['display_location']['country_iso3166'], wz['temperature_string'], wz['feelslike_string'], wz['weather'], wz['relative_humidity'], wz['observation_time'])
			bot.msg(target, buf)
			return
	bot.msg(target, "Error retrieving weather.")

def helpweather():
	return ['WEATHER <location>', 'Gets weather data from Weather Underground']
def helpw():
	return ['W <location>', 'Alias for WEATHER.']
