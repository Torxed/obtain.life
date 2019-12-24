import json, dns.resolver

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
	if not b'mode' in headers[b'path_payload']: return None
	if not b'domain' in headers[b'path_payload']: return None

	mode = headers[b'path_payload'][b'mode'].decode('UTF-8')
	domain = headers[b'path_payload'][b'domain'].decode('UTF-8')

	log(f'Starting verification for domain {domain} via {mode}', level=4, origin='verify')

	if mode == 'DNS':
		for ns_record in dns.resolver.query(domain, 'NS'):
			print(f'Found NS server {ns_record} for {domain}')
			for ns_ip in dns.resolver.query(ns_record.to_text(), 'A'):
				nameserver = dns.resolver.Resolver()
				nameserver.nameservers = [ns_ip.to_text()]
				print(f'Querying {ns_record} ({ns_ip.to_text()}) for obtain.life.{domain}')
				try:
					for txt_record in nameserver.query(f'obtain.life.{domain}', 'TXT'):
						challenge = txt_record.to_text().strip('" ;.')
						if challenge in datastore['claims'][domain]:
							mail_config = {
								'DOMAIN' : domain,
								'SSH_MAIL_USER_FROM' : 'no-reply', # without @
								'SSH_MAIL_USER_FROMDOMAIN' : 'obtain.life', # without @
								'SSH_MAIL_USER_TO' : datastore['claims'][domain][challenge].split('@',1)[0],
								'SSH_MAIL_USER_TODOMAIN' : datastore['claims'][domain][challenge].split('@',1)[1],
								'RAW_TIME' : time(),
								'SUBJECT' : f'You have claimed domain: {domain}',
								'TRY_ONE_MAILSERVER' : False,
								'TEXT_TEMPLATE' : TEXT_TEMPLATE,
								'HTML_TEMPLATE' : HTML_TEMPLATE,
								'DKIM_KEY' : "/etc/sshmailer/sshmailer.pem",
								'PASSWORD_LINK' : 'https://obtain.life/OTP/?challenge='+uid()
							}

							email(mail_config)

							return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
								'status' : 'success'
							}), 'UTF-8')
				except dns.resolver.NXDOMAIN:
					pass
	elif mode == 'HTTPS':
		pass

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'failed',
		'message' : f'No DNS record located at domain {domain}'
	}), 'UTF-8')