import logging, signal, shutil, json
from hashlib import sha512
from collections import OrderedDict as OD
from time import time
from os import walk, urandom
from os.path import isfile
from systemd.journal import JournalHandler

import hmac
import hashlib

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

from slimHTTP import slimhttpd
from spiderWeb import spiderWeb
from slimSocket import slimSocket

if isfile('datstore.json'):
	with open('datstore.json', 'r') as fh:
		log('Loading sample datastore from {{datstore.json}}', origin='STARTUP', level=5)
		datastore = safedict(json.load(fh))

		#datastore = dict_to_safedict(datastore)
else:
	log(f'Starting with a clean database (reason: couldn\'t find {{datastore.json}})', origin='STARTUP', level=5)
	datastore = safedict()

if not 'id' in datastore:
	datastore['id'] = {
		'22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2' : {
			'name' : 'scientist.cloud',
			'contact' : 'evil@scientist.cloud',
			'alg' : 'HS256',
			'secret' : '02f9cdb4f740b2b043d09fc91136058390b4f6ab4cf4701c93f6819e72895bc8',
			'users' : {
				'anton' : {'password' : 'test'}
			},
			'auth_sessions' : {

			}
		}
	}

if not 'domains' in datastore:
	datastore['domains'] = {
		'scientist.cloud' : '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2'
	}

if not 'tokens' in datastore: datastore['tokens'] = {}
if not 'blocks' in datastore: datastore['blocks'] = {}

def gen_id(length=256):
	return sha512(urandom(length)).hexdigest()

def save_datastore():
	if isfile('datastore.json'):
		shutil.move('datastore.json', 'datastore.json.bkp')

	with open('datstore.json', 'w') as fh:
		log('Saving datastore to {{datstore.json}}', origin='save_datastore', level=5)
		json.dump(datastore, fh)

def HMAC_256(data, key):
	signature = hmac.new(bytes(key , 'utf-8'), msg=bytes(data , 'utf-8'), digestmod = hashlib.sha256).hexdigest().upper()
	return signature

def signature_check(domain_id, data, key):
	if not data['alg'] == datastore['id'][domain_id]['alg']: return None
	if not data['sign']: return None

	if data['alg'] == 'HS256':
		client_signature = data['sign']

		del(data['sign'])
		print(f'Signing [{key}]:', [json.dumps(data, separators=(',', ':'))])
		server_signature = HMAC_256(json.dumps(data, separators=(',', ':')), key)
		data['sign'] = client_signature

		if not server_signature or server_signature.lower() != client_signature.lower():
			return server_signature

		return True

	return None

def allowed_user(client):
	if client.addr in datastore['blocks']: return False
	return True

def block(client):
	datastore['blocks'][client.addr] = time()

class parser():
	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		if not allowed_user(client):
			log(f'Client {client} is blocked, ignoring request.', level=4, origin='parser.parse')
			return None

		print(data)
		if not 'alg' in data: return None
		if not 'sign' in data or not data['sign']: return None
		if not 'domain' in data: data['domain'] = 'obtain.life'

		domain_id = datastore['domains'][data['domain']]
		key = datastore['id'][domain_id]['secret']
		server_signature = signature_check(domain_id, data, key)
		if server_signature is not True:
			log(f'Invalid signature from user {client}, expected signature: {server_signature} but got {data["sign"]}.', level=3, origin='parser.parse')
			block(client)
			return None

		for result in signed_parse(client, data, headers, fileno, addr, *args, **kwargs):
			yield result
			
def signed_parse(client, data, headers, fileno, addr, *args, **kwargs):
	## If we've gotten here, it means the signature of the packet is varified.
	## There for, we can treat the client-data as trusted for it's own domain.
	domain_id = datastore['domains'][data['domain']]

	if '_module' in data and data['_module'] == 'auth':
		if not 'username' in data: return None
		if not 'password' in data: return None

		if not data['username'] in datastore['id'][domain_id]['users']:
			log(f'User probing attempt from {client}', level=2, origin='signed_parse')
			block(client)
			return None

		username = data['username']
		if data['password'] != datastore['id'][domain_id]['users'][username]['password']:
			log(f'Password spraying from {client} on account {username}@{data["domain"]}', level=2, origin='signed_parse')
			block(client)
			return None

		print('Logged in!')
		token = gen_id()
		datastore['tokens'][token] = {'user' : data['username'], 'time' : time(), 'domain' : domain_id}

		response = {'_module' : 'auth', 'status' : 'success', 'token' : token, 'sign' : None, 'alg' : data['alg']}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

		yield response

websocket = spiderWeb.upgrader({'default': parser()})
http = slimhttpd.http_serve(upgrades={b'websocket': websocket}, port=1337)
https = slimhttpd.https_serve(upgrades={b'websocket': websocket}, port=1338, cert='cert.pem', key='key.pem')
socket = slimSocket.socket_serve(port=1339, parsers=websocket.parsers)

while 1:
	for handler in [http, https, socket]:
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