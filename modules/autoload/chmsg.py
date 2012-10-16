from classes import *
from util import *

name = 'channel messaging'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('SAY', 3, say, 1, helpsay)
	cache.hookcmd('ACT', 3, act, 1, helpact)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('SAY')
	cache.unhookcmd('ACT')

def say(nick, target, params, bot, cache):
	bot.msg(target, params)

def act(nick, target, params, bot, cache):
	bot.msg(target, "\001ACTION %s\001" % (params))

def helpsay(): return ['SAY <#channel> <line>', 'Does a /ME.']
def helpact(): return ['ACT <#channel> <line>', 'Does a /ME <line>.']
