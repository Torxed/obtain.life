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

def uid(seed=None, bits=32):
	if not seed:
		seed = os.urandom(bits) + bytes(str(time()), 'UTF-8')
	return hashlib.sha512(seed)

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


if not 'domains' in datastore: datastore['domains'] = {}
if not 'id' in datastore:
	datastore['id'] = {}
	
	for domain in ('obtain.life', 'scientist.cloud'):
		secret_file = None
		if os.path.isdir('./secrets') and isfile(f'./secrets/{domain0}.json'):
			secret_file = f'./secrets/{domain}.json'
		elif os.path.isdir('/etc/obtain.life/secrets') and isfile(f'./etc/obtain.life/secrets/{domain}-json'):
			secret_file = f'./etc/obtain.life/secrets/{domain}-json'

		domain_id = uid()
		datastore['domains'][domain] = domain_id
		if secret_file:
			log(f'Loading secrets for {domain} in {secret_file}')
			with open(secret_file, 'r') as fh:
				try:
					datastore['id'][domain_id] = json.load(fh)
				except:
					log(f'Invalid JSON format in {secret_file}', level=2, origin='startup')
		else:
			datastore['id'][domain_id] = {
				"name" : domain,
				"contact" : "evil@scientist.cloud",
				"alg" : "HS256",
				"secret" : uid(),
				"service_secret" : uid(),
				"users" : {
					"anton" : {"username" : "anton",
								"password" : "test",
								"friendly_name" : "Anton Hvornum",
								"display_picture" : "https://avatars1.githubusercontent.com/u/861439?s=460&v=4"}
				},
				"auth_sessions" : {

				},
				"subscribers" : {

				}
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
	if type(data) == dict: data = json.dumps(data, separators=(',', ':'))
	if type(data) != bytes: data = bytes(data, 'UTF-8')
	if type(key) != bytes: key = bytes(key, 'UTF-8')
	print(f'Signing with key: {key}')
	print(json.dumps(json.loads(data.decode('UTF-8')), indent=4))

	signature = hmac.new(key, msg=data, digestmod = hashlib.sha256).hexdigest().upper()
	return signature

def service_signature_check(domain_id, data, key, auto_generated_fields={}):
	original_values = {**data}
	if not data['alg'] == datastore['id'][domain_id]['alg']: return None
	if not data['sign']: return None
	if not data['service_sign']: return None

	if data['alg'] == 'HS256':
		service_sign = data['service_sign']
		del(data['service_sign'])
		del(data['sign'])
		for field in auto_generated_fields:
			del(data[field])

		print(f'Signing with key: {key}')
		print(json.dumps(data, indent=4, separators=(',', ':')))

		server_signature = HMAC_256(json.dumps(data, separators=(',', ':')), key)
		data['service_sign'] = service_sign

		for key, val in original_values.items():
			data[key] = val

		if not server_signature or server_signature.lower() != service_sign.lower():
			return server_signature

		return True

	return None

def signature_check(domain_id, data, key):
	if not data['alg'] == datastore['id'][domain_id]['alg']: return None
	if not data['sign']: return None


	if data['alg'] == 'HS256':
		client_signature = data['sign']

		del(data['sign'])
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

		print('***', data)
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

		## Notify the backends:
		backend_notification = {'_module' : 'auth', 'status' : 'success', 'user' : datastore['id'][domain_id]['users'][username], 'domain' : data['domain'], 'token' : token, 'alg' : data['alg']}
		backend_notification['sign'] = HMAC_256(backend_notification, datastore['id'][domain_id]['secret'])

		for b_fileno in datastore['id'][domain_id]['subscribers']:
			print(f'Sending notification to subscriber {b_fileno},', datastore['id'][domain_id]['subscribers'][b_fileno]['sock'])
			datastore['id'][domain_id]['subscribers'][b_fileno]['sock'].send(backend_notification)

		datastore['tokens'][token] = {'user' : data['username'], 'time' : time(), 'domain' : domain_id}

		response = {'_module' : 'auth', 'status' : 'success', 'token' : token, 'sign' : None, 'alg' : data['alg']}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

		yield response

	elif '_module' in data and data['_module'] == 'register':
		auto_generated_fields = set()
		if not 'service' in data: data['service'] = 'user'
		if not 'friendly_name' in data:
			auto_generated_fields.add('friendly_name')
			data['friendly_name'] = ':'.join([str(x) for x in addr])

		if data['service'] == 'user':
			pass # Not allowed yet
		elif data['service'] == 'backend':
			if not 'service_sign' in data: return None

			key = datastore['id'][domain_id]['service_secret']
			server_signature = service_signature_check(domain_id, data, key, auto_generated_fields=auto_generated_fields)

			if server_signature is not True:
				log(f'Invalid service signature from endpoint {client}, expected signature: {server_signature} but got {data["service_sign"]}.', level=3, origin='parser.signed_parse')
				block(client)
				return None

			print(f'Service is subscribed on fileno {fileno}, identity {client}')
			datastore['id'][domain_id]['subscribers'][fileno] = {'sock' : client, 'addr' : addr, 'friendly_name' : data['friendly_name']}

			response = {'_module' : 'register', 'status' : 'success', 'domain' : data['domain'], 'friendly_name' : data['friendly_name']}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

			yield response

		elif data['service'] == 'domain':
			pass
			# Email user a challenge.
			# Once the user presses the verification link, the verification process starts.

websocket = spiderWeb.upgrader({'default': parser()})
http = slimhttpd.http_serve(upgrades={b'websocket': websocket}, port=1337)
https = slimhttpd.https_serve(upgrades={b'websocket': websocket}, port=1338, cert='cert.pem', key='key.pem')
socket = slimSocket.socket_serve(port=1339, parsers=websocket.parsers, cert='ca.crt', key='ca.key')

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
						if not client.keep_alive:
							client.close()