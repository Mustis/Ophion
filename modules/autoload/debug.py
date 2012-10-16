from classes import *
from util import *

name = 'debug'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('EXEC', 8, doexec, 1, helpexec, isadmin=True)
	cache.hookcmd('EVAL', 8, doeval, 1, helpeval, isadmin=True)
	cache.hookcmd('RAW', 8, raw, 2, helpraw, isadmin=True)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('EXEC')
	cache.unhookcmd('EVAL')
	cache.unhookcmd('RAW')

def doexec(nick, target, params, bot, cache):
	try: exec(params)
	except Exception as e: bot.msg(nick, "Exception! "+str(e))
	else: bot.msg(nick, "Done.")
def doeval(nick, target, params, bot, cache):
	ret = None
	try: ret = eval(params)
	except Exception as e: bot.msg(nick, "Exception! "+str(e))
	else: bot.msg(nick, "Return: %s" % (ret))
def raw(nick, target, params, bot, cache):
	pieces = params.split()
	if pieces[0] == "*":
		for bot in cache.bots.values():
			if bot.online: bot.raw(' '.join(pieces[1:]))
	else:
		bid = toint(pieces[0])
		if cache.isonline(bid):
			cache.bots[bid].raw(' '.join(pieces[1:]))
		else:
			bot.msg(nick, "No such bot, or offline.")


def helpexec(): return ['EXEC <code>', 'Runs Python <code> in exec, and prints the exception (if any).']
def helpeval(): return ['EVAL <code>', 'Runs Python <code> in eval, and prints the return or exception.']
def helpraw(): return ['RAW <bid> <line>', 'Sends <line> to the server from bot BID.']
