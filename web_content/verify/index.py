import json, dns.resolver

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
	<title>Set password</title>
	<style type="text/css">
		body {{
			background-color: #000;

			color: #fff;
			font-family: sans-serif;
			font-size:13px;
			font-weight: bold;

			margin: 0px;
			padding: 0px;

			display: flex;
			flex-direction: column;
			justify-content: center;
			align-items: center;

			width: 100%;
			height: 100%;

			position: absolute;
		}}

		.container {{
			display: flex;
			flex-direction: column;
			margin-top: auto;
			margin-bottom: auto;

			background-color: rgba(120, 120, 120, 0.85);
			overflow: hidden;

			border-top-left-radius: 10px;
			border-top-right-radius: 10px;
		}}

			.header {{
				background-color: #282828;
				border-bottom: 1px solid #222222;
				padding: 10px;
				color: #8CBEB2;
			}}

			label {{
				padding: 5px;
			}}

			label:before {{
				content: "Admin account: ";
				color: #8CBEB2;
			}}

			.inputField {{
				border: 1px solid #272727;
				border-radius: 4px;
				padding: 5px;
				margin: 2px;
			}}

			.inputs {{
				display: flex;
				flex-direction: column;
			}}

			.inputs, span {{
				padding: 10px;
			}}

			b {{
				color: #f0bd60;
			}}
	</style>
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
			The claim will be void and discarded. <br>
			You have 10 minutes before this session is automatically discarded.
		</span>
	
		<div class="inputs">
			<label>anton@hvornum.se</label>
			<input type="text" id="password" class="inputField" placeholder="Password for admin account">
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
							return {}, HTML_TEMPLATE.format(DOMAIN=domain, OTP=otp)
						print(f'Challenge "{challenge}" for domain "{domain}" does not match any in {datastore["claims"][domain]}')
				except dns.resolver.NXDOMAIN:
					pass
	elif mode == 'HTTPS':
		pass

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'failed',
		'message' : f'No DNS record located at domain {domain}'
	}), 'UTF-8')