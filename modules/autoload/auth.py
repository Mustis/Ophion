from classes import *
from util import *

name = 'auth'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('AUTH', 0, auth, 0, helpauth, isadmin=True)
	cache.hookcmd('WHOIS', 1, whois, 1, helpwhois, isadmin=True)
	cache.hookcmd('WHOAMI', 0, whoami, 0, helpwhoami, isadmin=True)
	cache.hooknum('354', rep_who)
	cache.hooknum('353', rep_names)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('AUTH')
	cache.unhookcmd('WHOIS')
	cache.unhookcmd('WHOAMI')
	cache.unhooknum('354', rep_who)
	cache.unhooknum('353', rep_names)

def auth(nick, target, params, bot, cache):
	bot.raw("WHO %s n%%hna" % (nick))
	bot.msg(nick, "Looking up your auth...")

def whois(nick, target, params, bot, cache):
	lookup = params.split()[0]
	if lookup[0] == '*':
		if cache.users[nick].access >= 1:
			lookup = lookup[1:]
			bid = toint(lookup)
			bot2 = None
			if bid is None:
				if lookup in cache.botsByNick:
					bot2 = cache.botsByNick[lookup]
			else:
				if bid in bot2s:
					bot2 = bot2s[bid]
			if bot2 is not None:
				bot.msg(nick, "Bot #%d ..." % (bot2.id))

				if bot2.nick: bot.msg(nick, "- nick: %s" % (bot2.nick))
				else: bot.msg(nick, "- doesn't know it's nick")

				if bot2.online: bot.msg(nick, "- is online")
				else: bot.msg(nick, "- is offline")

				if bot2.mainbot: bot.msg(nick, "- is the mainbot")
				else: bot.msg(nick, "- is not the mainbot")

				if len(bot2.rawqueue) != 0: bot.msg(nick, "- has %d lines in queue" % (len(bot2.rawqueue)))
				else: bot.msg(nick, "- has an empty queue")

				if len(bot2.chans) != 0: bot.msg(nick, "- in %s" % (' '.join([chan.name for chan in bot2.chans.values()])))
				else: bot.msg(nick, "- is in no channels.")

				bot.msg(nick, "End info for bot #%d" % (bot2.id))
			else:
				bot.msg(nick, "No such bot %s" % (lookup))
	elif lookup[0] != '#':
		if lookup in cache.users:
			auth = cache.users[lookup].auth
			access = cache.users[lookup].access
			bot.msg(nick, "%s is #%s (access: %d)" % (lookup, auth, access))
		else:
			bot.msg(nick, "%s is not a known user." % (lookup))
			return
	else:
		auth = lookup[1:]
		curs = cache.dbc.cursor()
		curs.execute("SELECT level FROM admins WHERE username = %s", (auth,))
		row = curs.fetchone()
		if row is not None:
			bot.msg(nick, "%s (access: %d)" % (lookup, row['level']))
		else:
			bot.msg(nick, "%s is unknown." % (lookup))

def whoami(nick, target, params, bot, cache):
	if nick in cache.users and cache.users[nick].access != -1:
		bot.msg(nick, "You are %s (#%s access: %d)" % (nick, cache.users[nick].auth, cache.users[nick].access))

		curs = cache.dbc.cursor()
		curs.execute("SELECT chans.chname AS ch, chusers.level AS level FROM chans, chusers WHERE chans.id = chusers.chid AND chusers.authname = %s", (cache.users[nick].auth,))
		rows = curs.fetchall()
		if len(rows) != 0:
			bot.msg(nick, "-- CHANNELS:")
			for row in rows:
				bot.msg(nick, "%s - level %d" % (row['ch'], row['level']))
			bot.msg(nick, "-- END OF CHANNELS")
	else:
		bot.msg(nick, "You are %s (unknown auth)" % (nick))

def rep_who(line, bot): # :<server.tld> 354 <self> <host> <nick> <auth>
	pieces = line.split()
	host = pieces[3]
	nick = pieces[4]
	auth = pieces[5]
	if nick not in cache.users:
		cache.users[nick] = User(nick)
	user = cache.users[nick]
	user.host = host
	cache.users[nick].authed(auth)

def rep_names(line, bot): # :<server.tld> 353 <self> = <#chan> :jrunyon @Ophion +BiohZn @Q +DimeCadmium
	pieces = line.split()
	chan = pieces[4]
	nicksidx = line.find(':', 1)
	nicks = line[nicksidx+1:].split()
	for nick in nicks:
		mode = nick[0]
		if mode == '@' or mode == '+':
			chlevel = mode
			nick = nick[1:]
		else:
			chlevel = None
		if nick != bot.nick: bot.joined(chan, nick, chlevel)
		

def helpauth(): return ['AUTH', 'Requests the bot to look up your account.']
def helpwhois(): return ['WHOIS <nick|#auth>', 'Shows info about an account with the bot.']
def helpwhoami(): return ['WHOAMI', 'Shows info about your account with the bot.']
