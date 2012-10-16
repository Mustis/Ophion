from classes import *
from util import *

import time, os, random, json
from threading import Timer
from traceback import print_exc

name = 'trivia'
author = 'John Runyon'
version = '1'

questions = []
points = {}

aqinterval = 10 # seconds from question end -> next question
qhinterval = 30 # seconds from question prompt -> hint
hainterval = 30 # seconds from hint -> question end

def init(cache):
	global questions, points
	cache.currmod = __name__
	cache.trivia = {}

	try:
		qfile = open(cache.triviapath+"/questions.txt", 'r')
	except IOError as e:
		print_exc(None, cache.excfile)
		return True
	questions = qfile.readlines()
	qfile.close()

	try:
		ptsfile = open(cache.triviapath+"/points.json", 'r')
	except IOError as e:
		print_exc(None, cache.excfile)
		return True
	points = json.load(ptsfile)
	ptsfile.close()

	cache.hookcmd('TRIVIA', 1, trivia, 1, helptrivia)
	cache.hookcmd('T', 0, t, 1, helpt)
def deinit(cache, reloading=False):
	global questions, points
	cache.currmod = __name__

	ptsfile = open(cache.triviapath+"/points.json", 'w')
	json.dump(points, ptsfile, indent=4)
	ptsfile.close()

	del questions
	del points
	del cache.trivia
	cache.unhookcmd('TRIVIA')

def _loadQuestion():
	tdict = {}
	line = random.choice(questions)
	parts = line.split('~', 2)
	tdict['question'] = parts[0]
	tdict['answer'] = parts[1].lower()
	if len(parts) == 3: tdict['flags'] = parts[2].split('~')
	else: tdict['flags'] = []
	return tdict
def _sendQuestion(cache, chan):
	tdict = cache.trivia[chan]['tdict']
	cache.chans[chan].bot.msg(chan, "Next question: %s" % (tdict['question']))
	timer = Timer(qhinterval, _sendHint, kwargs={'cache': cache, 'chan': chan})
	cache.trivia[chan]['timer'] = timer
	cache.trivia[chan]['timertype'] = '_sendHint'
def _sendHint(cache, chan):
	tdict = cache.trivia[chan]['tdict']
	pieces = tdict['answer'].split(' ')
	hintpieces = []
	for piece in pieces:
		if piece == '': continue
		plen = len(piece)
		reveal = int(round(plen*0.40))
		if reveal < 2: reveal = 2
		if reveal > plen: reveal = plen

		revealpos = []
		for i in range(reveal):
			pos = random.randint(0, plen-1)
			while pos in revealpos:
				pos = random.randint(0, plen-1)
			revealpos.append(pos)
		hiddenpieces = []
		for i in range(plen):
			if i in revealpos:
				hiddenpieces.append(piece[i])
			elif not piece[i].isalnum():
				hiddenpieces.append(piece[i])
			else:
				hiddenpieces.append('*')
		hintpieces.append(''.join(hiddenpieces))
	hint = ' '.join(hintpieces)
	cache.chans[chan].bot.msg(chan, "Hint: %s" % (hint))

def trivia(nick, target, params, bot, cache):
	chan = target.lower()
	if params == 'start':
		tdict = _loadQuestion()
		timer = Timer(aqinterval, _sendQuestion, kwargs={'cache': cache, 'chan': chan})
		cache.trivia[chan] = {'tdict': tdict, 'timer': timer, 'timertype': '_sendQuestion'}
	elif params == 'stop':
		cache.trivia[chan]['timer'].cancel()
		del cache.trivia[chan]
def t(nick, target, params, bot, cache):
	chan = target.lower()
	guess = params.lower()
	if chan not in cache.trivia:
		bot.msg(nick, "Trivia isn't running in %s!" % (chan))
	elif nick not in cache.users or cache.users[nick] == '':
		bot.msg(nick, "You must be AUTH'ed and recognized by me! Try !AUTH")
	else:
		pass #TODO

def helptrivia(): return ['TRIVIA <#channel> start|stop', 'Starts or stops trivia.']
def helpt(): return ['T <#channel> <answer>', 'Attempt to answer a trivia question. You must be authed with the bot. If no reply, guess was incorrect.']
