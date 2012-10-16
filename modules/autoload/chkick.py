from classes import *
from util import *

name = 'channel kick'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('KICK', 3, kick, 1, helpkick)
	cache.hookcmd('BAN', 3, ban, 1, helpban)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('KICK')
	cache.unhookcmd('BAN')

def kick(nick, target, params, bot, cache):
	pieces = params.split(None, 1)
	reason = "Requested by %s" % (nick)
	if len(pieces) == 2:
		reason = "%s (%s)" % (pieces[1], reason)
	bot.raw("KICK %s %s :%s" % (target, pieces[0], reason))

def ban(nick, target, params, bot, cache):
	bot.raw("MODE %s +b %s" % (target, pieces[0]))
	bot.msg(nick, "Done.")

def helpkick(): return ['KICK <#channel> [<reason>]', 'Kicks <user>']
def helpban(): return ['BAN <hostmask>', 'Bans <hostmask>. (Doesn\'t kick)']
