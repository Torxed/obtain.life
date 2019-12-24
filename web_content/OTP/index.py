import json
from time import time

"""
<h3>Accounts:</h3>
<span>
	You can add, manage and update user accounts at <a href="https://obtain.life">obtain.life</a>.<br>
	Simply log in with this admin account to do so<br>
	<i>(or promote others to administrators and let them do it)</i>
</span>
<h3>Domain configuration:</h3>
<span>
	You can also tweak configurations for your domain.<br>
	For instance,<br>
	<ul>
		<li>Set password expire times</li>
		<li>Account expire dates</li>
	</ul>
	Best of luck //Obtain.life
</span>
"""

TEXT_TEMPLATE = """
You have successfully claimed {DOMAIN}.

You can add, manage and update user accounts at <a href="https://obtain.life">obtain.life</a>.
Simply log in with this admin account, or promote others to administrators and let them do it.

You can also tweak configurations for your domain, such as password expirey, account expire dates etc.

Best of luck //Obtain.life
"""

HTML_TEMPLATE = """
<html>
	<head>
		<title>You have successfully claimed {DOMAIN}</title>
	</head>
	<body>
		<div>
			<h3>Accounts:</h3>
			<span>
				You can add, manage and update user accounts at <a href="https://obtain.life">obtain.life</a>.
				Simply log in with this admin account, or promote others to administrators and let them do it.
			</span>
			<h3>Domain configuration:</h3>
			<span>
				You can also tweak configurations for your domain, such as password expirey, account expire dates etc.

				Best of luck //Obtain.life
			</span>
		</div>
	</body>
</html>
"""

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

	domain_id = uid()
	datastore['domains'][domain] = domain_id
	datastore['id'][domain_id] = {
		"name" : domain,
		"contact" : admin,
		"alg" : "HS256",
		"secret" : uid(),
		"service_secret" : uid(),
		"users" : {
			admin_user : {"username" : admin_user,
						"password" : data['password'],
						"friendly_name" : admin_user}
		},
		"auth_sessions" : {

		},
		"subscribers" : {

		}
	}

	datastore['id'][datastore['domains']['obtain.life']]['users'][admin] = {
		"username" : admin_user,
		"password" : data['password'],
		"friendly_name" : admin_user}

	token = uid()
	datastore['tokens'][token] = {'user' : admin_user, 'time' : time(), 'domain' : domain}

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'success',
		'message' : f'Domain has been fully claimed by {admin}.',
		'token' : token
	}), 'UTF-8')