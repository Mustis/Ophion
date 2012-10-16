from classes import *
from util import *

name = 'channel modes'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('CHANLEV', 1, chanlev, 0, helpchanlev)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('CHANLEV')

def chanlev(nick, target, params, bot, cache):
	pieces = params.split()
	user = cache.users[nick]
	chan = cache.chans[target]

	if len(pieces) == 0:
		bot.msg(nick, "-- ACCESS LIST FOR %s" % (target))
		for authname, access in chan.alist.items():
			bot.msg(nick, "%-15s %s" % (authname, access))
		bot.msg(nick, "-- END OF ACCESS LIST")
	elif len(pieces) == 1:
		if pieces[0][0] == '#':
			auth = pieces[0][1:]
			bot.msg(nick, "Auth %s has level %s on %s" % (auth, chan.alist[auth], target))
		elif pieces[0] in cache.users:
			auth = cache.users[pieces[0]].auth
			bot.msg(nick, "Nick %s has level %s on %s" % (pieces[0], chan.alist[auth], target))
		else:
			bot.msg(nick, "%s is unknown." % (pieces[0]))
	elif len(pieces) == 2:
		auth = user.auth
		if auth in chan.alist and chan.alist[auth] >= 4:
			level = chan.alist[auth]
			if pieces[0][0] == '#':
				targauth = pieces[0][1:]
			elif pieces[0] in cache.users:
				targauth = cache.users[pieces[0]].auth
			else:
				bot.msg(nick, "%s is unknown." % (pieces[0]))
				return
			targlev = toint(pieces[1])
			if targlev is None or targlev > 5:
				bot.msg(nick, "Invalid level %d." % (targlev))
				return
			if level != 5:
				if targauth in chan.alist and chan.alist[targauth] >= level:
					noaccess(bot, nick, True)
					return
				if targlev >= level:
					noaccess(bot, nick, True)
					return
			if targlev != 0:
				chan.alist[targauth] = targlev
				curs = cache.dbc.cursor()
				curs.execute("REPLACE INTO chusers(chid, authname, level) VALUES (%s, %s, %s)", (chan.id, targauth, targlev))
				curs.close()
			elif targauth in chan.alist:
				del chan.alist[targauth]
				curs = cache.dbc.cursor()
				curs.execute("DELETE FROM chusers WHERE chid = %s AND authname = '%s'" % (chan.id, targauth))
				curs.close()
			bot.msg(nick, "Done.")
		else:
			noaccess(bot, nick, True)
	else:
		bot.msg(nick, "Invalid syntax. Usage: CHANLEV <#channel> [<nick|#auth> [<level>]]")

def helpchanlev():
	return ['CHANLEV <#channel> [<nick|#auth> [<level>]]', 'Change or view access.']
