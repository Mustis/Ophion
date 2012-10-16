from classes import *
from util import *

name = 'admin messaging'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('ADMINSEND', 2, send, 3, helpsend, isadmin=True)
	cache.hookcmd('ADMINACT', 2, act, 3, helpact, isadmin=True)
def deinit(cache):
	cache.currmod = __name__
	cache.unhookcmd('ADMINSEND')
	cache.unhookcmd('ADMINACT')

def send(nick, target, params, bot, cache):
	pieces = params.split()
	sbid = pieces[0]
	bid = toint(sbid)
	target = pieces[1]
	msg = ' '.join(pieces[2:])
	if sbid == "*":
		for bot in cache.bots.values():
			if bot.online: bot.msg(target, msg)
	elif cache.isonline(bid):
		cache.bots[bid].msg(target, msg)
	else:
		bot.msg(nick, "No such bot, or offline.")
def act(nick, target, params, bot, cache):
	pieces = params.split()
	sbid = pieces[0]
	bid = toint(sbid)
	target = pieces[1]
	msg = ' '.join(pieces[2:])
	if sbid == "*":
		for bot in cache.bots.values():
			if bot.online: bot.raw("PRIVMSG %s :\1ACTION %s\1" % (target, msg))
	elif cache.isonline(bid):
		cache.bots[bid].raw("PRIVMSG %s :\1ACTION %s\1" % (target, msg))
	else:
		bot.msg(nick, "No such bot, or offline.")


def helpsend(): return ['ADMINSEND <bid> <nick|#channel> <msg>', 'Sends a PRIVMSG (#channel) or NOTICE (nick).']
def helpact(): return ['ADMINACT <bid> <nick|#channel> <msg>', 'Sends an ACTION (/me).']
