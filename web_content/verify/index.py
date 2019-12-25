import json, dns.resolver, urllib.request

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
	<title>Set password</title>
	<link rel="stylesheet" type="text/css" href="/resources/styles/mini.css">
	<script type="text/javascript">
		let OTP = '{OTP}';

		window.onload = function() {{
			document.querySelector('#submit').addEventListener('click', function() {{
				data = {{
					"password" : document.querySelector('#password').value,
					"OTP" : OTP
				}}

				const request = async () => {{
					const response = await fetch("/OTP/", {{
						method: 'POST', // or 'PUT'
						body: JSON.stringify(data),
						headers: {{
						  'Content-Type': 'application/json'
						}}
					}});
					const json = await response.json();
					
					if(typeof json['token'] !== 'undefined') {{
						localStorage.setItem('obtain.life.token', json['token']);
						window.location.href = '/portal/';
					}}
				}}

				request();
			}})
		}}
	</script>
</head>
<body>
	<div class="container">
		<div class="header">You've successfully verified {DOMAIN}</div>
		<span>
			You have one final step to claim {DOMAIN},<br>
			You must create a master password for your domain admin account.<br>
			<br>
			<b>Important:</b> If you close this window/tab without setting a password,<br>
			the claim will be void and discarded. <br>
			You have 10 minutes before this session is automatically discarded.
		</span>
	
		<div class="inputs">
			<label>{admin}</label>
			<input type="password" id="password" class="inputField" placeholder="Password for admin account">
			<button id="submit" class="inputField">Set Password</button>
		</div>
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

							otp = uid()
							datastore['OTPs'][otp] = {'domain' : domain, 'admin' : datastore['claims'][domain][challenge]}
							return {}, HTML_TEMPLATE.format(DOMAIN=domain, OTP=otp, admin=datastore['claims'][domain][challenge])
						print(f'Challenge "{challenge}" for domain "{domain}" does not match any in {datastore["claims"][domain]}')
				except dns.resolver.NXDOMAIN:
					pass
	elif mode == 'HTTPS':
		response = urllib.request.urlopen(f'https://{domain}/obtain.life.txt')
		challenge = response.read().decode('UTF-8').strip(' \n\r.;')
		if challenge in datastore['claims'][domain]:
			otp = uid()
			datastore['OTPs'][otp] = {'domain' : domain, 'admin' : datastore['claims'][domain][challenge]}
			return {}, HTML_TEMPLATE.format(DOMAIN=domain, OTP=otp, admin=datastore['claims'][domain][challenge])

		print(f'Challenge "{challenge}" for domain "{domain}" does not match any in {datastore["claims"][domain]}')

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'failed',
		'message' : f'No DNS record located at domain {domain}'
	}), 'UTF-8')