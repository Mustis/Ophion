#!/usr/bin/python

###
### Ophion Bot
### v1.00
### Copyright 2012 John Runyon
### <https://github.com/Mustis/Ophion>
###

## CONFIG
dbhost = 'localhost'
dbuser = 'bot'
dbpass = 'roboticism'
dbname = 'bot'
rootdir = '/home/bots/'
logfile = rootdir+'/output.log'
excfile = rootdir+'/exception.log'

oidfile = '/home/bots/.oidentd.conf'
identprefix = 'ophion' # ident will be <identprefix><bot ID#>

import socket, select, sys, os, signal, time
from threading import *
from traceback import print_exc

import MySQLdb, MySQLdb.cursors

from classes import *
from util import *

cache = Cache()

def quit(reason, restart=False):
	cache.quitting = True
	cache.mainBot.cmsg('fatal', "Shutting down because: %s" % (reason))
	time.sleep(1)
	for bot in cache.bots.values():
		bot.disconnect()
	for tkey in cache.timers.keys():
		cache.timers[tkey].cancel()
		del cache.timers[tkey]
	for modf in cache.modules:
		unloadmod(modf, cache, True)

	if restart:
		os.execv(sys.argv[0], sys.argv)
	sys.exit(0)
def sigHandle(signum, stack):
	quit("Signal: %d" % (signum))
def online(bid):
	return (bid in cache.bots and cache.bots[bid].online)
def toofew(bot, nick): # like: if len(params) < NEEDED: return toofew(bot, nick)
	bot.msg(nick, "Too few parameters for that command.")
	return False

def sendRaws():
	for bot in cache.bots.values():
		bot.sendRaws()
	if not cache.quitting:
		t = Timer(1, sendRaws)
		t.daemon = True
		if 'raws' in cache.timers: del cache.timers['raws']
		cache.timers['raws'] = t
		t.start()

def connectBots():
	curs = cache.dbc.cursor()
	curs.execute("SELECT 1")
	curs.close()

	connected = 0
	for bot in cache.bots.values():
		if not bot.online:
			ident = "%s%d" % (identprefix, bot.id)
			oid = open(oidfile, 'w')
			oid.write("global {\n\treply \"%s\"\n}" % ident)
			oid.close()
			if bot.connect(ident):
				bot.cmsg('info', "Connected")
				connected += 1
				if connected == 2:
					break

	if not cache.quitting:
		if connected < 2: interval = 300
		else: interval = 60
		t = Timer(interval, connectBots)
		t.daemon = True
		if 'conn' in cache.timers: del cache.timers['conn']
		cache.timers['conn'] = t
		t.start()

	return connected
def makeBots():
	curs = cache.dbc.cursor()
	curs.execute("SELECT id FROM bots")
	row = curs.fetchone()
	while row is not None:
		bot = Bot(row['id'])
		if row['id'] == 0:
			cache.mainBot = bot
			bot.mainbot = True
		cache.bots[row['id']] = bot
		row = curs.fetchone()

def fillCache():
	curs = cache.dbc.cursor()
	curs.execute("SELECT username, level FROM admins")
	row = curs.fetchone()
	while row is not None:
		cache.admins[row['username']] = row['level']
		row = curs.fetchone()
	curs.execute("SELECT chname FROM chans ORDER BY id LIMIT 2")
	rows = curs.fetchall()
	cache.ctrl = rows[0]['chname']
	cache.home = rows[1]['chname']
	curs.close()
	makeBots()

def parseCmd(bot, line, linepieces, msg, iscm):
	hostmask = linepieces[0][1:]
	fromnick = hostmask.split('!')[0]
	target = linepieces[2]
	pieces = msg.split()
	cmd = pieces[0].upper()
	if len(pieces) == 1: params = ''
	else: params = ' '.join(pieces[1:])

	ret = ""

	if cmd not in cache.cmds:
		noaccess(bot, fromnick)
		return ret
	else: ci = cache.cmds[cmd]

	if not ci['isadmin']:
		if fromnick not in cache.users:
			cache.users[fromnick] = User(fromnick)
		auth = cache.users[fromnick].auth
		if not iscm:
			if ci['reqchan']:
				target = pieces.pop(1).lower()
				params = ' '.join(pieces[1:])
			else:
				target = fromnick
		if target not in cache.chans:
			bot.msg(fromnick, "No such channel.")
			return ret 
		chan = cache.chans[target]
		if auth not in chan.alist or chan.alist[auth] < ci['level']:
			noaccess(bot, fromnick, True)
			return ret
		elif len(pieces)-1 < cache.cmds[cmd]['params']:
			toofew(bot, fromnick)
			return ret
		else:
			try: ret = cache.cmds[cmd]['func'](fromnick, target, params, chan.bot, cache)
			except Exception as e:
				print_exc(None, cache.excfile)
				bot.msg(fromnick, "An error occurred, sorry! Try again later.")
				cache.mainBot.cmsg('warn', "EXCEPTION! %r Caused by <%s> %s" % (e, fromnick, line))

	else: # admin/global command
		if fromnick in cache.users: glblevel = cache.users[fromnick].access
		else: glblevel = 0 
		if glblevel < ci['level']:
			noaccess(bot, fromnick)
		elif len(pieces)-1 < cache.cmds[cmd]['params']:
			toofew(bot, fromnick)
		else:
			try: ret = cache.cmds[cmd]['func'](fromnick, target, params, bot, cache)
			except Exception as e:
				print_exc(None, cache.excfile)
				bot.msg(fromnick, "An error occurred, sorry! Try again later.")
				cache.mainBot.cmsg('warn', "EXCEPTION! %r Caused by <%s> %s" % (e, fromnick, line))
	return ret

def _parse(bot, line):
	pieces = line.split()
	if pieces[1] == "PRIVMSG":
		target = pieces[2]
		msg = ' '.join(pieces[3:]).lstrip(':')
		if msg[0] == cache.trigger:
			return parseCmd(bot, line, pieces, msg[1:], True)
		elif target == bot.nick:
			return parseCmd(bot, line, pieces, msg, False)
	elif pieces[1] == "JOIN":
		nick = pieces[0][1:].split('!')[0]
		host = pieces[0][1:].split('@')[1]
		chname = pieces[2].lower()
		if chname in cache.chans:
			bot.joined(chname, nick)
	elif pieces[1] == "PART":
		nick = pieces[0][1:].split('!')[0]
		chname = pieces[2].lower()
		if chname in cache.chans:
			bot.parted(chname, nick)
	elif pieces[1] == "QUIT":
		nick = pieces[0][1:].split('!')[0]
		bot.quit(nick)
	elif pieces[1] == "NICK":
		fromnick = pieces[0][1:].split('!')[0]
		tonick = pieces[2][1:]
		cache.users[tonick] = cache.users[fromnick]
		del cache.users[fromnick]
		cache.users[tonick].nick = tonick
	elif pieces[0] == "PING":
		bot.rawnow("PONG %s" % (pieces[1]))
	elif pieces[0] == "ERROR":
		try: bot.disconnect()
		except: pass
	elif pieces[1] in cache.nums:
		for fn in cache.nums[pieces[1]]:
			try: fn(line, bot)
			except Exception as e:
				print_exc(None, cache.excfile)
				bot.msg(fromnick, "An error occurred, sorry! Try again later.")
				cache.mainBot.cmsg('warn', "EXCEPTION! %r Caused by <%s> %s" % (e, fromnick, line))

def parse(bot):
	line = bot.get().strip()
	return _parse(bot, line)


def loop():
	while True:
		ready = cache.poll.poll()
		for fde in ready:
			ret = ""
			if fde[0] == sys.stdin.fileno():
				line = sys.stdin.readline().strip()
				pieces = line.split(None, 2)
				if len(pieces) == 3 and pieces[1].isdigit():
					mode = pieces[0]
					bid = int(pieces[1])
					line = pieces[2]
					if mode.upper() == "IN": ret = _parse(cache.bots[bid], line)
					elif mode.upper() == "OUT": cache.bots[bid].rawnow(line)
					else: print "ERROR! <'IN'|'OUT'>:<bid>:<line>"
				else: print "ERROR! <'IN'|'OUT'>:<bid>:<line>"
			elif fde[0] in cache.botsByFD: # it's a bot
				bot = cache.botsByFD[fde[0]]
				if fde[1] & select.POLLERR or fde[1] & select.POLLHUP or fde[1] & select.POLLNVAL:
					bot.disconnect()
				else:
					ret = parse(bot)
			if ret == "QUIT": break
		else: continue
		break # if the "for" was broken, break the while as well.


signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGINT, sigHandle)

cache.excfile = open(excfile, 'a')

sys.path.append(rootdir+'/modules')
sys.path.append(rootdir+'/modules/autoload')
for modf in os.listdir(rootdir+'/modules/autoload'):
	if modf[-3:] == ".py":
		loadmod(modf[:-3], cache)

cache.dbc = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, cursorclass=MySQLdb.cursors.DictCursor)
fillCache()

cache.poll = select.poll()

cache.poll.register(sys.stdin.fileno(), select.POLLIN)

t = Timer(1, sendRaws)
t.daemon = True
cache.timers['raws'] = t
t.start()

connectBots()
t = Timer(60, connectBots)
t.daemon = True
cache.timers['conn'] = t
t.start()

loop()
