from classes import *
from util import *

name = 'module control'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('LOADMOD', 9, doloadmod, 1, helploadmod, isadmin=True)
	cache.hookcmd('UNLOADMOD', 9, dounloadmod, 1, helpunloadmod, isadmin=True)
	cache.hookcmd('RELOADMOD', 9, doreloadmod, 1, helpreloadmod, isadmin=True)
	cache.hookcmd('LISTMODS', 8, dolistmods, 0, helplistmods, isadmin=True)
def deinit(cache, reloading):
	if reloading:
		cache.currmod = __name__
		cache.unhookcmd('LOADMOD')
		cache.unhookcmd('UNLOADMOD')
		cache.unhookcmd('RELOADMOD')
		cache.unhookcmd('LISTMODS')
	else:
		return True # block unload

def doloadmod(nick, target, params, bot, cache):
	modf = params.split()[0]
	retcode = loadmod(modf, cache)
	if retcode == 0: bot.msg(nick, "Loaded %s successfully." % (modf))
	elif retcode == 1: bot.msg(nick, "Error loading %s: import error." % (modf))
	elif retcode == 2: bot.msg(nick, "Error loading %s: already loaded." % (modf))
def dounloadmod(nick, target, params, bot, cache):
	modf = params.split()[0]
	retcode = unloadmod(modf, cache)
	if retcode == 0: bot.msg(nick, "Unloaded %s successfully." % (modf))
	elif retcode == 1: bot.msg(nick, "Error unloading %s: module refused unload." % (modf))
	elif retcode == 2: bot.msg(nick, "Error unloading %s: not loaded." % (modf))
def doreloadmod(nick, target, params, bot, cache):
	modf = params.split()[0]
	retcode = reloadmod(modf, cache)
	if retcode == 0: bot.msg(nick, "Reloaded %s successfully." % (modf))
	else: bot.msg(nick, "Error reloading %s: %d" % (modf, retcode))

def dolistmods(nick, target, params, bot, cache):
	bot.msg(nick, "-- LISTMODS")
	for modf in cache.modules.keys():
		mod = cache.modules[modf]
		bot.msg(nick, "%-20s - %s" % (modf, mod.name))
	bot.msg(nick, "-- END LISTMODS")

def helploadmod(): return ['LOADMOD <module>', 'Loads "modules/<module>.py".', 'modctrl']
def helpunloadmod(): return ['UNLOADMOD <module>', 'Unloads "modules/<module>.py".']
def helpreloadmod(): return ['RELOADMOD <module>', 'Reloads "modules/<module>.py".']
def helplistmods(): return ['LISTMODS', 'List loaded modules.']
