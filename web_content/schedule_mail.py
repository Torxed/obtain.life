TEXT_TEMPLATE = """\
To claim a domain, one of two simple things is required.
Either add a TXT record on your DNS server, or place a .txt file in your web root
verifying that you have control over the domain you're trying to claim.
Below follows instructions for the two options.

DNS option:
  Add a TXT record called obtain.life.{DOMAIN}. to your domain {DOMAIN}.
  After that, click this link to begin the <u>DNS verification process</u>:

  * {DNS_URL}

HTTPS option:
  Your remote server needs to accept TLS (HTTPS) traffic, we will
  not try to verify against anything but TLS enabled servers.
  In your web-root, add the following .txt file:
  https://{DOMAIN}/obtain.life.txt

  Once that is done, click this link to begin the <u>HTTPS verification process</u>.
  * {HTTPS_URL}

In both cases, the value of the record/file should be:
  {challenge}

Once the verification process is complete, {SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN} will recieve
an email where instructions to set a password will be sent out.

Best of luck //Obtain Life IM team
"""

		HTML_TEMPLATE = """\
<html>
	<head>
		<title>Claim {DOMAIN}</title>
	</head>
	<body>
		<div>
			<h3>To claim a domain:</h3>
			<span>
				To claim a domain, one of two simple things is required.<br>
				Either add a TXT record on your DNS server, or place a .txt file in your web root
				verifying that you have control over the domain you're trying to claim.<br>
				Below follows instructions for the two options.<br>
			</span>
			<h4>DNS option:</h4>
			<span>
				Add a TXT record called <b>obtain.life.{DOMAIN}</b>. to your domain {DOMAIN}.<br>
  				After that, click this link to begin the <u>DNS verification process</u>:
  				<ul>
					<li>{DNS_URL}</li>
				</ul>
			</span>
			<h4>HTTPS option:</h4>
			<span>
				Your remote server needs to accept TLS (HTTPS) traffic,<br>
				<u>we will not try to verify against anything but TLS enabled servers</u>.<br>
				In your web-root, add the following .txt file:
				<ul>
					<li><a href="https://{DOMAIN}/obtain.life.txt">https://{DOMAIN}/obtain.life.txt</a></li>
				</ul>
				Once that is done, click this link to begin the <u>HTTPS verification process</u>.<br>
				<ul>
					<li>{HTTPS_URL}</li>
				</ul>
				In both cases, the value of the record/file should be:<br>
				<b>{challenge}</b><br>
				<br>
				Once the verification process is complete, {SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN} will recieve
				an email where instructions to set a password will be sent out.<br>
				<br>
				Best of luck <a href="https://obtain.life">//Obtain Life IM team</a>
			</span>
		</div>
	</body>
</html>"""

		configuration = {
			'DOMAIN' : data['claim'],
			'SIGN_DOMAIN' : 'obtain.life',
			'SSH_MAIL_USER_FROM' : 'no-reply', # without @
			'SSH_MAIL_USER_FROMDOMAIN' : 'obtain.life', # without @
			'SSH_MAIL_USER_TO' : data['admin'].split('@',1)[0],
			'SSH_MAIL_USER_TODOMAIN' : data['admin'].split('@',1)[1],
			'RAW_TIME' : time(),
			'SUBJECT' : f'Claim domain: {data["claim"]}',
			'TRY_ONE_MAILSERVER' : False,
			'TEXT_TEMPLATE' : TEXT_TEMPLATE,
			'HTML_TEMPLATE' : HTML_TEMPLATE,
			'DKIM_KEY' : "/etc/sshmailer/sshmailer.pem",
			'DNS_URL' : f'https://obtain.life/verify/?mode=DNS&domain={data["claim"]}',
			'HTTPS_URL' : f'https://obtain.life/verify/?mode=HTTPS&domain={data["claim"]}',
			'challenge' : challenge
		}