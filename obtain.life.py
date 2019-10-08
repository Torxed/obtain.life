import logging, signal, shutil
from slimHTTP import slimhttpd
from spiderWeb import spiderWeb
from hashlib import sha512
from collections import OrderedDict as OD
from time import time
from os import walk, urandom
from os.path import isfile
from systemd.journal import JournalHandler

def sig_handler(signal, frame):
	http.close()
	https.close()
	exit(0)
signal.signal(signal.SIGINT, sig_handler)

# Custom adapter to pre-pend the 'origin' key.
# TODO: Should probably use filters: https://docs.python.org/3/howto/logging-cookbook.html#using-filters-to-impart-contextual-information
class CustomAdapter(logging.LoggerAdapter):
	def process(self, msg, kwargs):
		return '[{}] {}'.format(self.extra['origin'], msg), kwargs

## == Setup logging:
logger = logging.getLogger() # __name__
journald_handler = JournalHandler()
journald_handler.setFormatter(logging.Formatter('[{levelname}] {message}', style='{'))
logger.addHandler(journald_handler)
logger.setLevel(logging.DEBUG)

def _log(*msg, origin='UNKNOWN', level=5, **kwargs):
	if level <= LOG_LEVEL:
		msg = [item.decode('UTF-8', errors='backslashreplace') if type(item) == bytes else item for item in msg]
		msg = [str(item) if type(item) != str else item for item in msg]
		log_adapter = CustomAdapter(logger, {'origin': origin})
		if level <= 1:
			log_adapter.critical(' '.join(msg))
		elif level <= 2:
			log_adapter.error(' '.join(msg))
		elif level <= 3:
			log_adapter.warning(' '.join(msg))
		elif level <= 4:
			log_adapter.info(' '.join(msg))
		else:
			log_adapter.debug(' '.join(msg))

class _safedict(dict):
	def __init__(self, *args, **kwargs):
		args = list(args)
		self.debug = False
		for index, obj in enumerate(args):
			if type(obj) == dict:
				m = safedict()
				for key, val in obj.items():
					if type(val) == dict:
						val = safedict(val)
					m[key] = val

				args[index] = m

		super(safedict, self).__init__(*args, **kwargs)

	def __getitem__(self, key):
		if not key in self:
			self[key] = safedict()

		val = dict.__getitem__(self, key)
		#if self.debug:
			#if type(val) == dict:
				#print('GET:', self, key)
				#print('     ', type(val), val)
		return val

	def __setitem__(self, key, val):
		if type(val) == dict:
			val = safedict(val)
		#	if self.debug:
				#print('SET:', self, key)
				#print('     ', type(val), val)
		#print(key, val)
		dict.__setitem__(self, key, val)

	def dump(self, *args, **kwargs):
		copy = safedict()
		for key in self.keys():
			val = self[key]
			if type(key) == bytes and b'*' in key: continue
			elif type(key) == str and '*' in key: continue
			elif type(val) == dict or type(val) == safedict: val = val.dump()
			elif key in ('password', 'secret', 'privkey'): val = '****'
			copy[key] = val
		return copy

	def copy(self, *args, **kwargs):
		return super(safedict, self).copy(*args, **kwargs)

__builtins__.__dict__['LOG_LEVEL'] = 4
__builtins__.__dict__['log'] = _log
__builtins__.__dict__['safedict'] = _safedict
__builtins__.__dict__['sockets'] = safedict()
__builtins__.__dict__['config'] = safedict({
	'slimhttp': {
		'web_root': './web_content',
		'index': 'index.html',
		'vhosts': {
			'obtain.life': {
				'web_root': './web_content',
				'index': 'index.html'
			}
		}
	}
})

if isfile('datstore.json'):
	with open('datstore.json', 'r') as fh:
		log('Loading sample datastore from {{datstore.json}}', origin='STARTUP', level=5)
		datastore = safedict(json.load(fh))

		#datastore = dict_to_safedict(datastore)
else:
	log(f'Starting with a clean database (reason: couldn\'t find {{datastore.json}})', origin='STARTUP', level=5)
	datastore = safedict()

if not 'guardians' in datastore: datastore['guardians'] = {
	'22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2' : {
		'name' : 'hvornum.se',
		'contact' : 'anton@hvornum.se',
		'secret' : '02f9cdb4f740b2b043d09fc91136058390b4f6ab4cf4701c93f6819e72895bc8',
		'users' : {
			'anton' : {'password' : 'domain'}
		}
	}
}
if not 'users' in datastore: datastore['users'] = {
	'anton' : {'password' : 'test'}
}
if not 'auth_sessions' in datastore: datastore['auth_sessions'] = {
	'22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2' : {
		# ...
	}
}
if not 'tokens' in datastore: datastore['tokens'] = {}

def gen_id(length=256):
	return sha512(urandom(length)).hexdigest()

def save_datastore():
	if isfile('datastore.json'):
		shutil.move('datastore.json', 'datastore.json.bkp')

	with open('datstore.json', 'w') as fh:
		log('Saving datastore to {{datstore.json}}', origin='save_datastore', level=5)
		json.dump(datastore, fh)

class parser():
	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		if '_module' in data:
			print(safedict(data).dump())
			if data['_module'] == 'auth':
				## !!!!
				## TODO: Error logging on all the return None, they should never happen !!
				if not 'username' in data and 'password' not in data: return None
				if type(data['username']) != str or type(data['password']) != str: return None
				if not '_app' in data:
					## == A simple login/shared domains
					## TODO: Think this one through, because once a access token is given.
					##       That token can be used by Company.A to access Company.B services.
					##       Could be solved by a callback
#					if not data['username'] in datastore['users']: return None
#
#					if datastore['users'][data['username']]['password'] == data['password']:
#						log(f"User {data['username'][:200]} logged in.", level=5, origin="AUTH", function="simple")
#						token = gen_id()
#						datastore['tokens'][token] = {'user' : data['username'], 'time' : time()}
#						yield {'_module' : 'auth', 'status' : 'success', 'token' : token}
#					else:
#						log(f"Failed login attempt for user '{data['username'][:200]}'", level=3, origin="AUTH", function="simple")
					return None
				else:
					## == A non-simple login with domain-soecific users
					if not data['_app'] in datastore['guardians']: return None
					if not data['username'] in datastore['guardians'][data['_app']]['users']: return None

					guardian = datastore['guardians'][data['_app']]
					if guardian['users'][data['username']]['password'] == data['password']:
						log(f"User '{data['username'][:200]}' beloging to guardian '{guardian['name'][:200]}' logged in.", level=5, origin="AUTH", function="simple")
						token = gen_id()
						datastore['tokens'][token] = {'user' : data['username'], 'time' : time()}
						yield {'_module' : 'auth', 'status' : 'success', 'token' : token}
					else:
						log(f"Failed login attempt for user '{data['username'][:200]}' beloging to guardian '{guardian['name'][:200]}'", level=3, origin="AUTH", function="simple")

			elif data['_module'] == 'register':
				if not '_guardian' in data: return None
				if not '_user' in data: return None
				if not '_secret' in data: return None
				if not data['_guardian'] in datastore['guardians']: return None
				if not data['_secret'] == datastore['guardians'][data['_guardian']]['_secret']: return None

				guardian = datastore['guardians'][data['_guardian']]

				if data['_user']['id'] in datastore['users'][data['_guardian']]:
					if 'protect' in data and data['protect']:
						log(f"Guardian {guardian['name']} was about to overwrite (but blocked): {data['_user']['id'][:200]}")
						yield {'_module' : 'register', 'status' : 'failed', 'reason' : 'User already exists, and you\'ve chosen protected mode on this user ID.'}
					else:
						log(f"Guardian {guardian['name']} is overwriting {data['_user']['id'][:200]}")
				else:
					log(f"Guardian {guardian['name']} is regestrating a user: {data['_user']['id'][:200]}")

				datastore['users'][data['_guardian']][data['_user']['id']] = data['_user']
				yield {'_module' : 'register', 'status' : 'successful'}

			elif data['_module'] == 'ping':
				if 'token' in data and data['token'] in datastore['tokens']:
					log(f'Token has been refreshed for user: {tokens[data["token"]]["user"]}', level=4, origin='PING')
					datastore['tokens'][data['token']]['time'] = time

				yield {'_module' : 'ping', 'status' : 'success', 'time' : time()}

			else:
				log(f'Module traversing detected from {addr}: {data["_module"][:200]}', level=3, origin='TRAP')
		else:
			log(f'Invalid data structure detected from {addr}: {str(data)[:200]}', level=3, origin='TRAP')

#websocket = spiderWeb.server({'default' : parser()}, address='127.0.0.1', port=1337)

websocket = spiderWeb.upgrader({'default': parser()})
http = slimhttpd.http_serve(upgrades={b'websocket': websocket}, port=1337)
https = slimhttpd.https_serve(upgrades={b'websocket': websocket}, port=1338, cert='cert.pem', key='key.pem')

while 1:
	for handler in [http, https]:
		client = handler.accept()

		#for fileno, client in handler.sockets.items():
		for fileno, event in handler.poll().items():
			if fileno in handler.sockets:  # If not, it's a main-socket-accept and that will occur next loop
				sockets[fileno] = handler.sockets[fileno]
				client = handler.sockets[fileno]
				if client.recv():
					response = client.parse()
					if response:
						try:
							client.send(response)
						except BrokenPipeError:
							pass
						client.close()