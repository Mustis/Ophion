from classes import *
from util import *

name = 'help'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('HELP', 0, dohelp, 0, helphelp, isadmin=True)
	cache.hookcmd('SHOWCOMMANDS', 0, showcommands, 0, helpshowcommands, isadmin=True)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('HELP')
	cache.unhookcmd('SHOWCOMMANDS')

def dohelp(nick, target, params, bot, cache):
	if len(params) == 0: showcommands(nick, target, params, bot, cache)
	else:
		thehelp = cache.gethelp(params.upper(), nick)
		if thehelp is not None:
			bot.msg(nick, '-- HELP for %s' % (params))
			bot.msg(nick, 'Syntax: %s' % (thehelp[0]))
			for theline in thehelp[1:]:
				bot.msg(nick, theline)
			bot.msg(nick, '-- End of HELP for %s' % (params))
		else:
			bot.msg(nick, "HELP for %s not available: no such command or not enough access." % (params))

def showcommands(nick, target, params, bot, cache):
	helps = []
	if nick in cache.users:
		access = cache.users[nick].access
	else:
		access = 0
	bot.msg(nick, '-- COMMAND LIST')
	for key in sorted(cache.cmds):
		cmd = cache.cmds[key]
		if access >= cmd['level']:
			cmdhelp = cmd['helpfunc']()
			if len(cmdhelp) == 3 and access >= 1:
				bot.msg(nick, "%-20s %s [module: %s]" % (cmdhelp[0], cmdhelp[1], cmdhelp[2]))
			else:
				bot.msg(nick, "%-20s %s" % (cmdhelp[0], cmdhelp[1]))
	bot.msg(nick, '-- End of COMMAND LIST')

def helphelp(): return ['HELP [<command>]', 'Requests help for a command, or shows a command list.']
def helpshowcommands(): return ['SHOWCOMMANDS', 'Shows a command list.']
