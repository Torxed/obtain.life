import json, os, hashlib
from time import time
from base64 import b64encode, b64decode

def response(root, path, payload, headers, *args, **kwargs):
	if type(payload) != bytes: return None
	data = payload.decode('UTF-8')

	try:
		data = json.loads(data)
	except:
		return None

	if not 'OTP' in data: return None # Block client
	if not 'password' in data: return None # Block client

	OTP = data['OTP']
	if not OTP in datastore['OTPs']: return None # Block client

	OTP_INFO = datastore['OTPs'][OTP]
	domain = OTP_INFO['domain']
	admin = OTP_INFO['admin']
	admin_user = admin.split('@', 1)[0]
	salt = os.urandom(8)
	password = b64encode(salt).decode('UTF-8')+'&'+hashlib.sha512(salt+bytes(data['password'], 'UTF-8')).hexdigest()

	domain_id = uid()
	datastore['domains'][domain] = domain_id
	datastore['id'][domain_id] = {
		"name" : domain,
		"contact" : admin,
		"alg" : "HS256",
		"secret" : short_uid(),
		"service_secret" : short_uid(),
		"users" : {
			admin_user : {"username" : admin_user,
						"password" : password,
						"email" : admin,
						#"domain" : domain,
						#"friendly_name" : admin_user,
						"roles" : [
							"obtain.life.admin"
						]}
		},
		"auth_sessions" : {

		},
		"subscribers" : {

		}
	}

	if not admin in datastore['id'][datastore['domains']['obtain.life']]['users']:
		datastore['id'][datastore['domains']['obtain.life']]['users'][admin] = {
			"username" : admin,
			"password" : password,
			"email" : admin, # Shadow copy this...
			"friendly_name" : admin_user,
			"roles" : ["domain.admin"],
			"obtain.life.username.map" : admin_user,
			"domain" : domain}

	token = uid()
	datastore['tokens'][token] = {'user' : admin_user, 'time' : time(), 'domain' : domain, 'shadow_username' : admin, 'shadow_domain' : 'obtain.life'}

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'success',
		'message' : f'Domain has been fully claimed by {admin}.',
		'token' : token
	}), 'UTF-8')