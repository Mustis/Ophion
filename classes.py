import socket, random, select
from collections import deque

from util import *

class User:
	def __init__(self, nick):
		self.nick = nick
		self.auth = ''
		self.access = 0
		self.alist = []
		self.commonchans = []
		self.host = None
	def __str__(self): return self.nick
	def __repr__(self): return "<User: %s (%d)>" % (self.nick, self.access)
	def authed(self, username):
		self.auth = username
		if username in cache.admins:
			self.access = cache.admins[username]
	def joined(self, chan):
		self.commonchans.append(chan)
	def parted(self, chan):
		if chan in self.commonchans: self.commonchans.remove(chan)
		if self.commonchans == []:
			self.auth = ''
			self.access = 0

class Channel:
	def __init__(self, name, bot, id):
		self.id = id
		self.name = name
		self.bot = bot

		self.triggers = {}

		self.alist = {}
		curs = cache.dbc.cursor()
		curs.execute("SELECT authname, level FROM chusers WHERE chid = %s", (self.id,))
		row = curs.fetchone()
		while row is not None:
			self.alist[row['authname']] = row['level']
			row = curs.fetchone()

		self.ops = []
		self.voices = []
		self.users = []
	def joined(self, user):
		self.users.append(user)
		user.joined(self.name)
	def parted(self, user):
		if user in self.users: self.users.remove(user)
		if user in self.ops: self.ops.remove(user)
		if user in self.voices: self.voices.remove(user)
		user.parted(self.name)
	def opped(self, user):
		self.ops.append(user)
	def voiced(self, user):
		self.voices.append(user)
	def __str__(self): return self.name
	def __repr__(self): return "<Chan: %s>" % (self.name)

class Bot:
	def __init__(self, id):
		self.id = id
		self.online = False
		self.chans = {}
		self.mainbot = False
		self.rawqueue = deque()

	def get(self):
		buf = ""
		chin = self.s.recv(1)
		while chin != "\n":
			buf += chin
			chin = self.s.recv(1)
		buf = buf.strip()
		print "<%d<%s" % (self.id, buf)
		return buf

	def sendRaws(self, count=2):
		if self.online:
			for i in range(count):
				try: line = self.rawqueue.popleft()
				except IndexError: return
				self.rawnow(line)
	def raw(self, line):
		self.rawqueue.append(line)
	def rawnow(self, line):
		self.s.sendall(line+"\r\n")
		print ">%d>%s" % (self.id, line)

	def msg(self, target, msg):
		msgs = msg.split("\n")
		for msg in msgs:
			if target[0] == '#':
				self.raw("PRIVMSG %s :%s" % (target, msg))
			else:
				self.raw("NOTICE %s :%s" % (target, msg))
	def cmsg(self, cmtype, msg, id=None):
		if id is None: id = self.id
		self.msg(cache.ctrl, cache.cmsgs[cmtype] % {'id': id, 'msg': msg})

	def joined(self, chname, nick, chlevel=None):
		chname = chname.lower()
		if chname not in self.chans and chname not in cache.chans:
			return

		self.raw("WHO %s n%%nah" % (nick))
		if nick not in cache.users: cache.users[nick] = User(nick)
		self.chans[chname].joined(cache.users[nick])
		if chlevel == "@":
			self.chans[chname].opped(cache.users[nick])
		if chlevel == "+":
			self.chans[chname].voiced(cache.users[nick])
	def parted(self, chname, nick):
		chname = chname.lower()
		if nick == self.nick:
			del self.chans[chname]
			del cache.chans[chname]
		elif chname in self.chans:
			self.chans[chname].parted(cache.users[nick])
	def quit(self, nick):
		if nick in cache.users:
			user = cache.users[nick]
			for ch in user.commonchans:
				cache.chans[ch].parted(user)
			del cache.users[nick]
		
	def disconnect(self):
		try: cache.mainBot.cmsg('warn', 'Disconnected!', self.id)
		except: pass
		try: self.rawnow("QUIT :Disconnected")
		except: pass
		try: self.s.shutdown(socket.SHUT_RDWR)
		except: pass
		try: self.s.close()
		except: pass
		for ch in self.chans.values():
			for user in ch.users:
				ch.parted(user)
		cache.poll.unregister(self.s.fileno())
		self.online = False

	def joinChans(self):
		curs = cache.dbc.cursor()
		curs.execute("SELECT id, chname FROM chans WHERE botid = %s", (self.id,))
		row = curs.fetchone()
		while row is not None:
			self.raw("JOIN %s" % (row['chname']))
			chan = Channel(row['chname'].lower(), self, row['id'])
			self.chans[row['chname'].lower()] = chan
			cache.chans[row['chname']] = chan
			row = curs.fetchone()
		curs.close()
	def connect(self, ident):
		curs = cache.dbc.cursor()
		curs.execute("SELECT irchost, ircport, ircpass, nick, vhost, realname, authname, authpass FROM bots WHERE id = %s", (self.id,))
		row = curs.fetchone()
		self.nick = row['nick']
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if row['vhost'] is not None:
			self.s.bind((row['vhost'], 0))
		self.s.connect((row['irchost'], row['ircport']))
		self.rawnow("NICK %s" % (self.nick))
		self.rawnow("USER %s * * :%s" % (ident, row['realname']))
		curs.close()
		while True:
			line = self.get()
			pieces = line.split()
			if pieces[0] == "PING":
				self.rawnow("PONG %s" % (pieces[1]))
			elif pieces[1] == "433":
				self.nick = self.nick+str(random.randrange(0,9))
				self.rawnow("NICK %s" % (self.nick))
			elif pieces[0] == "ERROR":
				self.online = False
				return False
			elif pieces[1] == "376" or pieces[1] == "422":
				break
		if row['authname'] is not None and row['authpass'] is not None:
			self.rawnow("AUTH %s %s" % (row['authname'], row['authpass']))
		self.rawnow("MODE %s +ix" % (self.nick))
		cache.poll.register(self.s.fileno(), select.POLLIN)
		cache.botsByFD[self.s.fileno()] = self
		cache.botsByNick[self.nick] = self
		self.joinChans()
		self.online = True
		return True
	def __str__(self): return self.nick
	def __repr__(self): return "<Bot%d: %s>" % (self.id, self.nick)

class Cache:
	# config
	lshost = '0.0.0.0'
	lsport = 13245 
	moduledata = '/home/bots/modules/'
	trigger = '!'
	cmsgs = { # %(id)d = bot id, %(msg)s = log message.
		'debug':        "\00303[\037DEBUG\037][%(id)d]: %(msg)s",
		'info':         "\00312[\037INFO\037][%(id)d]: %(msg)s",
		'warn':         "\00306[\037WARN\037][%(id)d]: %(msg)s",
		'fatal':        "\00304[\037FATAL\037][%(id)d]: %(msg)s",
	}


	# NOT config
	dbc = None
	ls = None
	admins = {}
	bots = {}
	botsByFD = {}
	botsByNick = {}
	mainBot = None
	home = None # homechan
	ctrl = None # ctrlchan
	modules = {}
	unmodules = {} # unloaded
	timers = {}
	quitting = False

	currmod = None
	cmds = {}
	nums = {}

	users = {}
	chans = {}

	def __init__(self):
		global cache
		cache = self

	def hooknum(self, num, func):
		try: self.nums[num].append(func)
		except: self.nums[num] = [func]
	def unhooknum(self, num, func):
		try: self.nums[num].remove(func)
		except: return False
		else: return True

	def hookcmd(self, cmd, level, func, params, helpfunc, isadmin=False, reqchan=True):
		self.cmds[cmd.upper()] = {'module': cache.currmod, 'func': func, 'level': level, 'params': params, 'helpfunc': helpfunc, 'isadmin': isadmin, 'reqchan': reqchan}
	def unhookcmd(self, cmd):
		try: del self.cmds[cmd]
		except: return False
		else: return True

	def gethelp(self, cmd, nick=None, user=None, access=None):
		if cmd in self.cmds:
			if self.cmds[cmd]['level'] == 0:
				return self.cmds[cmd]['helpfunc']()
			if nick is None and user is None:
				return self.cmds[cmd]['helpfunc']()
			elif nick is not None and nick in self.users and self.users[nick].access > self.cmds[cmd]['level']:
				return self.cmds[cmd]['helpfunc']()
			elif user is not None and user.access > self.cmds[cmd]['level']:
				return self.cmds[cmd]['helpfunc']()
			elif access is not None and access > self.cmds[cmd]['level']:
				return self.cmds[cmd]['helpfunc']()
		return None

	def isbot(self, bid):
		return (toint(bid) in self.bots)
	def isonline(self, bid):
		bid = toint(bid)
		return (bid in self.bots and self.bots[bid].online)
