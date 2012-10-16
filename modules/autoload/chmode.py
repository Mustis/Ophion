from classes import *
from util import *

name = 'channel modes'
def init(cache):
	cache.currmod = __name__
	cache.hookcmd('OP', 3, op, 0, helpop)
	cache.hookcmd('VOICE', 2, voice, 0, helpvoice)
	cache.hookcmd('DEOP', 0, deop, 0, helpdeop)
	cache.hookcmd('DEVOICE', 0, devoice, 0, helpdevoice)
	cache.hookcmd('DOWN', 0, down, 0, helpdown)
	cache.hooknum('MODE', modehook)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('OP')
	cache.unhookcmd('VOICE')
	cache.unhookcmd('DEOP')
	cache.unhookcmd('DEVOICE')
	cache.unhookcmd('DOWN')

def op(nick, target, params, bot, cache):
	if params == '': opnick = nick
	elif cache.chans[target].alist[cache.users[nick].auth] >= 4: opnick = params
	else:
		noaccess(bot, nick, True)
		return

	user = cache.users[nick]
	if user in cache.chans[target].ops:
		bot.msg(nick, "%s is already opped on %s" % (opnick, target))
	elif user in cache.chans[target].users:
		bot.raw("MODE %s +o %s" % (target, opnick))
		bot.msg(nick, "Done.")
	else:
		bot.msg(nick, "%s isn't on %s" % (opnick, target))
def voice(nick, target, params, bot, cache):
	if params == '': vnick = nick
	elif cache.chans[target].alist[cache.users[nick].auth] >= 3: vnick = params
	else:
		noaccess(bot, nick, True)
		return

	user = cache.users[nick]
	if user in cache.chans[target].voices:
		bot.msg(nick, "%s is already voiced on %s" % (vnick, target))
	elif user in cache.chans[target].users:
		bot.raw("MODE %s +v %s" % (target, vnick))
		bot.msg(nick, "Done.")
	else:
		bot.msg(nick, "%s isn't on %s" % (vnick, target))
def deop(nick, target, params, bot, cache):
	if params == '': opnick = nick
	elif cache.chans[target].alist[cache.users[nick].auth] >= 4: opnick = params
	else:
		noaccess(bot, nick, True)
		return

	user = cache.users[nick]
	if user in cache.chans[target].ops:
		bot.raw("MODE %s -o %s" % (target, opnick))
		bot.msg(nick, "Done.")
	elif user in cache.chans[target].users:
		bot.msg(nick, "%s isn't opped on %s" % (opnick, target))
	else:
		bot.msg(nick, "%s isn't on %s" % (opnick, target))
def devoice(nick, target, params, bot, cache):
	if params == '': vnick = nick
	elif cache.chans[target].alist[cache.users[nick].auth] >= 3: vnick = params
	else:
		noaccess(bot, nick, True)
		return

	user = cache.users[nick]
	if user in cache.chans[target].voices:
		bot.raw("MODE %s -v %s" % (target, vnick))
		bot.msg(nick, "Done.")
	elif user in cache.chans[target].users:
		bot.msg(nick, "%s isn't voiced on %s" % (vnick, target))
	else:
		bot.msg(nick, "%s isn't on %s" % (vnick, target))

def down(nick, target, params, bot, cache):
	user = cache.users[nick]
	if user in cache.chans[target].users:
		bot.raw("MODE %s -ov %s %s" % (target, nick, nick))
	else:
		bot.msg(nick, "You aren't on %s" % (target))


def modehook(line, bot): # :U!I@H MODE #chan +o-v DimeCadmium DimeCadmium
	pieces = deque(line.split()[2:]) # #chan +o-v DimeCadmium DimeCadmium
	chname = pieces.popleft().lower()
	if chname[0] != '#': return # usermode change
	if chname not in cache.chans:
		return
	chan = cache.chans[chname] # +o-v DimeCadmium DimeCadmium
	modes = pieces.popleft() # DimeCadmium DimeCadmium
	for i in modes:
		if i == '+':
			adding = True
		elif i == '-':
			adding = False
		elif i == 'o':
			nick = pieces.popleft()
			if nick not in cache.users: cache.users[nick] = User(nick)
			user = cache.users[nick]
			if adding: chan.ops.append(user)
			elif user in chan.ops: chan.ops.remove(user)
		elif i == 'v':
			nick = pieces.popleft()
			if nick not in cache.users: cache.users[nick] = User(nick)
			user = cache.users[nick]
			if adding: chan.voices.append(user)
			elif user in chan.voices: chan.voices.remove(user)

def helpop():
	return ['OP <#channel> [<nick>]', 'Ops you, or <nick>.']
def helpvoice():
	return ['VOICE <#channel> [<nick>]', 'Voices you, or <nick>.']
def helpdeop():
	return ['DEOP <#channel> [<nick>]', 'Deops you, or <nick>.']
def helpdevoice():
	return ['DEVOICE <#channel> [<nick>]', 'Devoices you, or <nick>.']
def helpdown():
	return ['DOWN <#channel>', 'Removes your op/voice.']
