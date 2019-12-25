import json, dns.resolver
from collections import defaultdict

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
	<title>Set up challenge</title>
	<link rel="stylesheet" type="text/css" href="/resources/styles/mini.css">
	<script type="text/javascript">
		window.onload = function() {{
			let challenge = localStorage.getItem('obtain.life.claim_challenge');

			if(!challenge)
				window.location.href = '/';

			document.querySelector('.challenge').innerHTML = challenge;

		}}
	</script>
</head>
<body>
	<div class="container">
		<div class="header">Create challenge for {DOMAIN}</div>
		<span>
			Your first step to claim {DOMAIN}, is that you need<br>
			to select one of two challenge methods so obtain.life<br>
			can verify that you own the above domain.<br>
			You do this by adding <b>the challenge</b>:
		</span>
		<div class="challenge"></div>
		<div class="notification">
			If you close this tab, <i>(or don't verify with a challenge within 24h)</i><br>
			a reminder e-mail will be sent to you.<br>
			<u>But only if your e-mail server support TLS</u> <i>(with a valid certificate)</i>.<br>
			Otherwise the claim will be void and discarded.
		</div>
		<span>
			The two methods will be described below in more detail.<br>
		</span>
		
		<h3>HTTPS method</h3>
		<span>
			The simplest method is to add a .txt file on your web server at<br>
			<a href="https://{DOMAIN}/obtain.life.txt">https://{DOMAIN}/obtain.life.txt</a><br>
			with the challenge-code mentioned above.<br>
			After doing so, click the <b>HTTPS</b> verification link below:<br>
		</span>
		<ul>
			<li>{HTTPS_URL}</li>
		</ul>

		<h3>DNS method</h3>
		<span>
			Second option is to add a TXT record to your DNS server.<br>
			The record must be called <b>obtain.life.{DOMAIN}</b><br>
			and contain the challenge mentioned above as it's content.<br>
			<br>
			Once the DNS is prepared, you can click the <b>DNS</b> verification link below:<br>
		</span>
		<ul>
			<li>{DNS_URL}</li>
		</ul>
	</div>
</body>
</html>
"""

def response(root, path, payload, headers, client, *args, **kwargs):
	if not b'domain' in headers[b'path_payload']: return None

	domain = headers[b'path_payload'][b'domain'].decode('UTF-8')

	if client.addr[0] in datastore['claims'][domain]:
		log(f'Showing verification details for domain {domain} to {client}', level=4, origin='verify')

		HTTPS_URL = f'<a target="_blank" href="https://obtain.life/verify/?domain={domain}&mode=HTTPS">https://obtain.life/verify/?domain={domain}&mode=HTTPS</a>'
		DNS_URL = f'<a target="_blank" href="https://obtain.life/verify/?domain={domain}&mode=DNS">https://obtain.life/verify/?domain={domain}&mode=DNS</a>'

		return {}, HTML_TEMPLATE.format_map(defaultdict(str, DOMAIN=domain, HTTPS_URL=HTTPS_URL, DNS_URL=DNS_URL))

	return {b'Content-Type' : b'application/json'}, bytes(json.dumps({
		'status' : 'failed',
		'message' : f'Your client (device) has no pending claims.'
	}), 'UTF-8')