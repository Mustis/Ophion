from classes import *
from util import *

name = 'quit'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('DIE', 8, die, 0, helpdie, isadmin=True)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('DIE')

def die(nick, target, params, bot, cache):
	return "QUIT"

def helpdie(): return ['DIE', 'Kills the bots.']
