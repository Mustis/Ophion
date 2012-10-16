from classes import *
from util import *

name = 'foobar'
author = 'John Runyon'
version = '1'
def init(cache):
	cache.currmod = __name__
#cache.hookcmd('COMMAND',level,cmdfn,params,helpfn,isadmin=False,reqchan=True)
	cache.hookcmd('FOO', 0, foo, 0, helpfoo)
	cache.hookcmd('BAR', 1, bar, 0, helpbar, isadmin=True)
	cache.hookcmd('BAZ', 0, baz, 0, helpbaz, reqchan=False)
	cache.hookcmd('HELLO', 0, hello, 1, helphello)
def deinit(cache, reloading=False):
	cache.currmod = __name__
	cache.unhookcmd('FOO')
	cache.unhookcmd('BAR')
	cache.unhookcmd('BAZ')
	cache.unhookcmd('HELLO')

def foo(nick, target, params, bot, cache):
	bot.msg(nick, "Foo to you too! (nick)")
	bot.msg(target, "Foo to you too! (target)")
def bar(nick, target, params, bot, cache):
	bot.msg(nick, "Bar to you too! (nick)")
	bot.msg(target, "Bar to you too! (target)")
def baz(nick, target, params, bot, cache):
	bot.msg(nick, "Baz to you too! (nick)")
	bot.msg(target, "Baz to you too! (target)")
def hello(nick, target, params, bot, cache):
	bot.msg(nick, "Hello, %s! (nick)" % (params))
	bot.msg(target, "Hello, %s! (target" % (params))

# ['COMMAND <params>', 'Help description']
def helpfoo(): return ['FOO <#channel>', "'FOO', 0, foo, 0, helpfoo"]
def helpbar(): return ['BAR', "'BAR', 1, bar, 0, helpbar, isadmin=True"]
def helpbaz(): return ['BAZ', "'BAZ', 0, baz, 0, helpbaz, reqchan=False"]
def helphello(): return ['HELLO', "'HELLO', 0, hello, 1, helphello"]
