import logging, signal, shutil, json
from hashlib import sha512
from collections import OrderedDict as OD
from time import time
from os import walk, urandom
from os.path import isfile, isdir
from systemd.journal import JournalHandler
from mailer import email as _email
from base64 import b64encode, b64decode
from random import randint

## https://support.google.com/a/answer/2956491?hl=en&authuser=1

import hmac
import hashlib

def sig_handler(signal, frame):
	http.close()
	https.close()

	with open('datastore.json', 'w') as fh:
		log('Saving datastore to {{datastore.json}}', origin='SHUTDOWN', level=5)
		json.dump(datastore, fh)
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

def _uid(seed=None, bits=32):
	if not seed:
		seed = urandom(bits) + bytes(str(time()), 'UTF-8')
	return hashlib.sha512(seed).hexdigest().upper()

def _short_uid(seed=None, bits=32):
	if not seed:
		seed = urandom(bits) + bytes(str(time()), 'UTF-8')
	return hashlib.sha1(seed).hexdigest().upper()

def _allowed_user(client):
	if client.addr in datastore['blocks']: return False
	return True

def _block(client):
	datastore['blocks'][client.addr] = time()
	return None

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
			
			if not 'include_sensitives' in kwargs and key in ('password', 'secret', 'privkey', 'service_secret'): val = None
			copy[key] = val
		return copy

	def dumps(self, *args, **kwargs):
		self.dump(*args, **kwargs)

	def copy(self, *args, **kwargs):
		return super(safedict, self).copy(*args, **kwargs)

__builtins__.__dict__['LOG_LEVEL'] = 4
__builtins__.__dict__['log'] = _log
__builtins__.__dict__['email'] = _email
__builtins__.__dict__['safedict'] = _safedict
__builtins__.__dict__['sockets'] = safedict()
__builtins__.__dict__['uid'] = _uid
__builtins__.__dict__['block'] = _block
__builtins__.__dict__['allowed_user'] = _allowed_user
__builtins__.__dict__['short_uid'] = _short_uid
__builtins__.__dict__['config'] = safedict({
	'slimhttp': {
		'web_root': './web_content',
		'index': 'index.html',
		'vhosts': {
			'obtain.life': {
				'web_root': './web_content',
				'index': ['index.html', 'index.py']
			}
		}
	}
})

from slimHTTP import slimhttpd
from spiderWeb import spiderWeb
from slimSocket import slimSocket

if isfile('datastore.json'):
	with open('datastore.json', 'r') as fh:
		log('Loading sample datastore from {{datastore.json}}', origin='STARTUP', level=5)
		try:
			_datastore = safedict(json.load(fh))
		except:
			_datastore = safedict()
		#datastore = dict_to_safedict(datastore)
else:
	log(f'Starting with a clean database (reason: couldn\'t find {{datastore.json}})', origin='STARTUP', level=5)
	_datastore = safedict()

__builtins__.__dict__['datastore'] = _datastore

if not 'domains' in datastore: datastore['domains'] = {}
if not 'id' in datastore:
	datastore['id'] = {}
	
	for domain in ('obtain.life', 'scientist.cloud'):
		secret_file = None
		if isdir('./secrets') and isfile(f'./secrets/{domain}.json'):
			secret_file = f'./secrets/{domain}.json'
		elif isdir('/etc/obtain.life/secrets') and isfile(f'./etc/obtain.life/secrets/{domain}-json'):
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
								"password" : "YcciKR9A8es=&dcda8bd5e9a905d76aa2982b4ab8728b80a8c78fe7fdefa36c6d8000f2c3bf7a01c73907009a70219ce23905af73efb19d178d42c3fe4f1cad7529f4dea233e1",
								"friendly_name" : "Anton Hvornum",
								"roles" : [
									"obtain.life.admin"
								],
								"domain" : "obtain.life",
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

	with open('datastore.json', 'w') as fh:
		log('Saving datastore to {{datastore.json}}', origin='save_datastore', level=5)
		json.dump(datastore, fh)

def HMAC_256(data, key):
	#print(f'Signing with key: {key}')
	if type(data) == dict: data = json.dumps(data, separators=(',', ':'))
	if type(data) != bytes: data = bytes(data, 'UTF-8')
	if type(key) != bytes: key = bytes(key, 'UTF-8')
	#print(json.dumps(json.loads(data.decode('UTF-8')), indent=4))

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

class parser():
	domain_id = None
	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		if not allowed_user(client):
			log(f'Client {client} is blocked, ignoring request.', level=4, origin='parser.parse')
			return None

		print(json.dumps(data, indent=4))
		if not 'alg' in data: return None
		if not 'sign' in data or not data['sign']: return None
		if not 'domain' in data: data['domain'] = 'obtain.life'

		domain_id = datastore['domains'][data['domain']]
		self.domain_id = domain_id
		key = datastore['id'][domain_id]['secret']
		server_signature = signature_check(domain_id, data, key)
		if server_signature is not True:
			log(f'Invalid signature from user {client}, expected signature: {server_signature} but got {data["sign"]}.', level=3, origin='parser.parse')
			block(client)
			return None

		for result in self.signed_parse(client, data, headers, fileno, addr, *args, **kwargs):
			yield result
			
	def signed_parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		## If we've gotten here, it means the signature of the packet is varified.
		## There for, we can treat the client-data as trusted for it's own domain.

		if '_module' in data and data['_module'] == 'auth':
			for response in self.login(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == '2FA':
			for response in self.two_factor_auth(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'identity':
			for response in self.identity(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'certificate':
			for response in self.cerficiate(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'register':
			for response in self.register(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'claim':
			for response in self.claim(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'profile':
			for response in self.profile(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

		elif '_module' in data and data['_module'] == 'domain':
			for response in self.domain(client, data, headers, fileno, addr, *args, **kwargs):
				yield response

	def two_factor_auth(self, client, data, headers, fileno, addr, *args, **kwargs):
		domain_id = datastore['domains'][data['domain']]
		if not '2FA' in data: return None
		if not data['2FA'] in datastore['2FA']:
			log(f'2FA spraying from {client}', level=2, origin='2FA')

			response = {'status' : 'failed', '_module' : '2FA', 'message' : 'You\'ve issued a incorrect token.'}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])
			yield response
			return None

		code = datastore['2FA'][data['2FA']]['2FA']
		username = datastore['2FA'][data['2FA']]['user']
		domain = datastore['2FA'][data['2FA']]['domain']
		if time()-datastore['2FA'][data['2FA']]['issue_time'] > 60:
			log(f'2FA token has expired for {username} at {domain}', level=2, origin='2FA')
			del(datastore['2FA'][data['2FA']])

			response = {'status' : 'failed', '_module' : '2FA', 'message' : 'This token has expired.'}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])
			yield response
			return None

		if not data['code'] == code:
			log(f'User {username} @ {domain} has entered a incorrect 2FA code from {client}', level=3, origin='2FA')
			return None

		token = gen_id()

		## Notify the backends:
		backend_notification = {'_module' : 'auth', 'status' : 'success', 'user' : datastore['id'][domain_id]['users'][username], 'domain' : domain, 'token' : token, 'alg' : data['alg']}
		backend_notification['sign'] = HMAC_256(backend_notification, datastore['id'][domain_id]['secret'])

		for b_fileno in datastore['id'][domain_id]['subscribers']:
			print(f'Sending notification to subscriber {b_fileno},', datastore['id'][domain_id]['subscribers'][b_fileno]['sock'])
			datastore['id'][domain_id]['subscribers'][b_fileno]['sock'].send(backend_notification)

		if 'obtain.life.username.map' in datastore['id'][domain_id]['users'][username]:
			shadow_username = datastore['id'][domain_id]['users'][username]['obtain.life.username.map']
			datastore['tokens'][token] = {'user' : shadow_username, 'time' : time(), 'domain' : domain, 'shadow_username' : username, 'shadow_domain' : 'obtain.life'}
			log(f'Re-mapping user {username} to {shadow_username} at {domain}', level=4, origin='login')
		else:
			shadow_username = username
			datastore['tokens'][token] = {'user' : shadow_username, 'time' : time(), 'domain' : domain}


		response = {'_module' : 'auth', 'status' : 'success', 'token' : token, 'alg' : data['alg']}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

		yield response


	def login(self, client, data, headers, fileno, addr, *args, **kwargs):
		domain_id = datastore['domains'][data['domain']]
		if not 'username' in data: return None
		if not 'password' in data: return None

		if not data['username'] in datastore['id'][domain_id]['users']:
			log(f'User probing attempt from {client}', level=2, origin='signed_parse')
			block(client)
			return None

		username = data['username']
		db_password = datastore['id'][domain_id]['users'][username]['password']
		salt, password = db_password.split('&', 1)

		if hashlib.sha512(b64decode(salt)+bytes(data['password'], 'UTF-8')).hexdigest() != password:
			log(f'Password spraying from {client} on account {username}@{data["domain"]}', level=2, origin='signed_parse')
			block(client)
			return None

		_2FA = randint(1000, 9999)
		_2FA_SERIAL = short_uid()
		datastore['2FA'][_2FA_SERIAL] = {'2FA' : _2FA, 'user' : username, 'domain' : data['domain'], 'issue_time' : time()}

		### EMAIL HERE
		TEXT_TEMPLATE = f"""
Here is your 2FA token for device {client.addr}.

{_2FA}

Best wishes //Obtain.life
"""

		HTML_TEMPLATE = f"""
<html>
	<head>
		<title>2FA token for device {client.addr}</title>
	</head>
	<body>
		<div>
			<span>
				Here is your 2FA token for device {client.addr}.
			</span>
			<br>
			<span>
				{_2FA}
			</span>
			<br>
			<span>
				Best wishes //Obtain.life
			</span>
		</div>
	</body>
</html>
"""

		contact_mail = datastore['id'][domain_id]['users'][username]['email']

		mail_config = {
			'SSH_MAIL_USER_FROM' : 'no-reply', # without @
			'SSH_MAIL_USER_FROMDOMAIN' : 'obtain.life', # without @
			'SSH_MAIL_USER_TO' : contact_mail.split('@',1)[0],
			'SSH_MAIL_USER_TODOMAIN' : contact_mail.split('@',1)[1],
			'RAW_TIME' : time(),
			'SUBJECT' : f'2FA token for device {client.addr}',
			'TRY_ONE_MAILSERVER' : False,
			'TEXT_TEMPLATE' : TEXT_TEMPLATE,
			'HTML_TEMPLATE' : HTML_TEMPLATE,
			'DKIM_KEY' : "/etc/sshmailer/sshmailer.pem",
			'SIGN_DOMAIN' : 'obtain.life'
		}

		email(mail_config)
		response = {'_module' : 'auth', 'status' : 'success', '2FA' : _2FA_SERIAL, 'alg' : data['alg']}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

		yield response

	def register(self, client, data, headers, fileno, addr, *args, **kwargs):
		domain_id = datastore['domains'][data['domain']]
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

			log(f'Backend {client} is subscribed to events on domain {data["domain"]}', level=4, origin='register')
			datastore['id'][domain_id]['subscribers'][fileno] = {'sock' : client, 'addr' : addr, 'friendly_name' : data['friendly_name']}

			response = {'_module' : 'register', 'status' : 'success', 'domain' : data['domain'], 'friendly_name' : data['friendly_name']}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

			yield response

	def subscribe(self, client, data, headers, fileno, addr, *args, **kwargs):
		pass

	def certificate(self, client, data, headers, fileno, addr, *args, **kwargs):
		pass

	def identity(self, client, data, headers, fileno, addr, *args, **kwargs):
		pass

	def domain(self, client, data, headers, fileno, addr, *args, **kwargs):
		if not 'token' in data: return None #block(client)
		if not data['token'] in datastore['tokens']:
			# Block client
			response = {'_module' : 'domain', 'status' : 'failed', 'alg' : data['alg'], 'message' : 'Invalid token'}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][self.domain_id]['secret'])

			log(f'{client} tried accessing domain information without a correct access token', level=3, origin='domain')

			yield response
			return None

		#datastore['tokens'][token] = {'user' : data['username'], 'time' : time(), 'domain' : domain_id}
		token_info = datastore['tokens'][data['token']]
		domain = token_info['domain']
		domain_id = datastore['domains'][domain]
		who = token_info['user']

		if 'obtain.life.admin' in datastore['id'][domain_id]['users'][who]['roles']:
			response = {'status' : 'success', '_module' : 'domain', 'domain' : datastore['id'][domain_id].dump(include_sensitives=True)}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

			yield response
			return None

		response = {'status' : 'failed', '_module' : 'domain', 'message' : 'Account roles prohibits exposing the secret.'}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])
		yield response

	def profile(self, client, data, headers, fileno, addr, *args, **kwargs):
		domain_id = datastore['domains'][data['domain']]
		if not 'token' in data: return None
		if not data['token'] in datastore['tokens']:
			# Block client
			response = {'_module' : 'profile', 'status' : 'failed', 'alg' : data['alg'], 'message' : 'Invalid token'}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

			log(f'Invalid token recieved by {client}, token: {data["token"]}', level=2, origin='profile')
			yield response
			return None

		myself = True
		token_info = datastore['tokens'][data['token']]
		user = token_info['user']
		domain = token_info['domain']
		domain_id = datastore['domains'][domain]

		if 'new_pwd' in data:
			if myself:
				db_old_password = datastore['id'][domain_id]['users'][user]['password']
				salt, old_password = db_old_password.split('&', 1)

				if hashlib.sha512(b64decode(salt)+bytes(data['old_pwd'], 'UTF-8')).hexdigest() == old_password:
					salt = urandom(8)
					new_password = b64encode(salt).decode('UTF-8')+'&'+hashlib.sha512(salt+bytes(data['new_pwd'], 'UTF-8')).hexdigest()

					if 'shadow_username' in token_info:
						shadow_domain_id = datastore['domains'][token_info['shadow_domain']]
						datastore['id'][shadow_domain_id]['users'][token_info['shadow_username']]['password'] = new_password
					datastore['id'][domain_id]['users'][user]['password'] = new_password

					del(datastore['tokens'][data['token']])
					token = gen_id()
					datastore['tokens'][token] = {'user' : user, 'time' : time(), 'domain' : domain}
					response = {'status' : 'success', 'alg' : data['alg'], '_module' : 'profile', 'change' : 'new_pwd', 'token' : token}

					yield response
				else:
					log(f'{client} is trying to change password without correct old password.', level=2, origin='profile')
					response = {'status' : 'failed', '_module' : 'profile', 'alg' : data['alg'], 'message' : 'Wrong old password supplied. To many failed attempts will lead to a account deactivation.'}
					response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

					yield response
			else:
				log(f'{client} is trying to change password for another user.', level=2, origin='profile')
				response = {'status' : 'failed', '_module' : 'profile', 'alg' : data['alg'], 'message' : 'Can not change passwords for other accounts.'}
				response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

				yield response
		else:
			if myself:
				response = {'status' : 'success', 'alg' : data['alg'], '_module' : 'profile', 'account_id' : user, 'profile' : datastore['id'][domain_id]['users'][user].dump()}
			else:
				response = {'status' : 'success', 'alg' : data['alg'], '_module' : 'profile', 'profile' : datastore['id'][domain_id]['users'][user].dump()}
			response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

			yield response

	def claim(self, client, data, headers, fileno, addr, *args, **kwargs):
		if not 'admin' in data: return None
		if not 'claim' in data: return None
		if data["claim"] in datastore['domains']:
			log(f'Re-claim attempt on domain {data["claim"]} by {client}', level=3, origin='claim')
			return None # Already claimed

		domain_id = datastore['domains'][data['domain']]
		log(f'{data["admin"]} is claiming {data["claim"]}.', level=4, origin="claim")

		if not 'claims' in datastore: datastore['claims'] = {}
		if not data['claim'] in datastore['claims']: datastore['claims'][data['claim']] = {}

		## Create a challenge slot for this domain, and point it to a admin.
		challenge = short_uid()
		print(f"Challenge for domain '{data['claim']}' is: {challenge}")
		datastore['claims'][data['claim']][challenge] = data['admin']
		datastore['claims'][data['claim']][client.addr[0]] = challenge

		response = {'_module' : 'claim', 'status' : 'success', 'domain' : data['claim'], 'challenge' : challenge, 'challenge_page' : '/challenge/'}
		response['sign'] = HMAC_256(json.dumps(response, separators=(',', ':')), datastore['id'][domain_id]['secret'])

		yield response

websocket = spiderWeb.upgrader({'default': parser()})
http = slimhttpd.http_serve(upgrades={b'websocket': websocket}, port=1337)
https = slimhttpd.https_serve(upgrades={b'websocket': websocket}, port=1338, cert='cert.pem', key='key.pem')
socket = slimSocket.socket_serve(port=1339, parsers=websocket.parsers, cert='2019-12-15.pem', key='2019-12-15.key')

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