from traceback import print_exc

def toint(s):
	i = None
	try: i = int(s)
	except: pass
	return i

def noaccess(bot, nick, chcmd=False):
	if chcmd:
		bot.msg(nick, "You don't have enough access to do that.")
	else:
		bot.msg(nick, "No such command or not enough access.")

#            except Exception as e:
#               print_exc(None, cache.excfile)
#               bot.msg(fromnick, "An error occurred, sorry! Try again later.")
#               cache.mainBot.cmsg('warn', "EXCEPTION! %r Caused by <%s> %s" % (e, fromnick, line))
def loadmod(modf, cache, reloading=False):
	# return: 0=success, 1=import error, 2=already loaded, 3=reload() failed
	if modf in cache.modules:
		return 2
	elif modf in cache.unmodules:
		mod = cache.unmodules[modf]
		try:
			reload(mod)
		except Exception as e:
			print "! reload"
			print_exc(None, cache.excfile)
			return 1
		try:
			if mod.init(cache):
				print "not mod.init(cache)"
				cache.excfile.write("%s refused init - returned True\n" % (modf))
				return 1
		except Exception as e:
			print "! init"
			print_exc(None, cache.excfile)
			return 1
		del cache.unmodules[modf]
	else:
		try:
			mod = __import__(modf)
		except Exception as e:
			print "! import"
			print_exc(None, cache.excfile)
			return 1
		try:
			if mod.init(cache):
				cache.excfile.write("%s refused init - returned True\n" % (modf))
		except Exception as e:
			print "! init"
			print_exc(None, cache.excfile)
			return 1
	cache.modules[modf] = mod
	return 0
def unloadmod(modf, cache, reloading=False):
	# return: 0=success, 1=refused unload, 2=not loaded
	if modf not in cache.modules:
		return 2
	else:
		try:
			ret = cache.modules[modf].deinit(cache, reloading)
		except Exception as e:
			print_exc(None, cache.excfile)
			return 1
		if ret:
			return 1
		else:
			cache.unmodules[modf] = cache.modules[modf]
			del cache.modules[modf]
			return 0
def reloadmod(modf, cache):
	# return: 0 = success; 1,2=unload error; 3,4,5=load error
	unloadret = unloadmod(modf, cache, True)
	if unloadret != 0: return unloadret
	loadret = loadmod(modf, cache, True)
	if loadret != 0: return loadret+2
	return 0
