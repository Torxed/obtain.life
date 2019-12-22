#!/usr/bin/python

## Requirements:
#  * python-dnspython
#  * python-dkim
#  * python-pygeoip

import smtplib, dns.resolver, os, logging, psutil, socket, ssl, dkim, json
from time import time, localtime
from hashlib import md5
from systemd.journal import JournalHandler
from sys import argv
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from os.path import isfile, dirname, isdir
from json import load as jload, dump as jdump

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

def log(*msg, origin='UNKNOWN', level=5, **kwargs):
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

def load_text_template():
	return """\
To claim a domain, one of two things is required.
Either add a DNS record or place a TXT file in your web root
verifying that you have control over the domain you're trying
to claim.

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

def load_html_template():
	return """\
<html>
	<head>
		<title>Claim {DOMAIN}</title>
	</head>
	<body>
		<div>
			<h3>To claim a domain:</h3>
			<span>
				To claim a domain, one of two things is required.<br>
				Either add a DNS record or place a TXT file in your web root
				verifying that you have control over the domain you're trying
				to claim.
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

def sign_email(email, configuration, selector='default', domain=None):
	if not domain: domain = configuration['DOMAIN']
	if type(selector) != bytes: selector = bytes(selector, 'UTF-8')
	if type(domain) != bytes: domain = bytes(domain, 'UTF-8')

	if not isdir(dirname(configuration['DKIM_KEY'])):
		log('Missing DKIM key: {DKIM_KEY}'.format(**configuration), level=3, origin='mailer')
		return None 
	if not isfile(configuration['DKIM_KEY']):
		log('Missing DKIM key: {DKIM_KEY}'.format(**configuration), level=3, origin='mailer')
		return None

	with open(configuration['DKIM_KEY'], 'rb') as fh:
		dkim_private_key = fh.read()

	sig = dkim.sign(message=bytes(email.as_string(), 'UTF-8'),
					selector=selector,
					domain=domain,
					privkey=dkim_private_key,
					include_headers=["To", "From", "Subject"])

	return sig.lstrip(b"DKIM-Signature: ").decode('UTF-8')

def email(configuration):
	configuration['HASH'] = md5(bytes('{SSH_MAIL_USER_FROM}@{SSH_MAIL_USER_FROMDOMAIN}+{SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN}'.format(**configuration), 'UTF-8')).hexdigest()
	configuration['Message-ID'] = '<{RAW_TIME}.{HASH}@{SSH_MAIL_USER_FROMDOMAIN}>'.format(**configuration)

	## TODO: https://support.google.com/mail/answer/81126
	## TODO:(DKIM) https://russell.ballestrini.net/quickstart-to-dkim-sign-email-with-python/
	## TODO:(S/MIME) https://tools.ietf.org/doc/python-m2crypto/howto.smime.html
	## TODO: https://support.rackspace.com/how-to/create-an-spf-txt-record/
	##
	## https://toolbox.googleapps.com/apps/checkmx/check?domain={DOMAIN}&dkim_selector=
	## https://github.com/PowerDNS/pdns/issues/2881

	email = MIMEMultipart('alternative')
	email['Subject'] = configuration['SUBJECT']
	email['From'] = "Obtain Life <{SSH_MAIL_USER_FROM}@{SSH_MAIL_USER_FROMDOMAIN}>".format(**configuration)
	email['To'] = "<{SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN}>".format(**configuration)
	email['Message-ID'] = configuration['Message-ID']
	email.preamble = configuration['SUBJECT']

	text = load_text_template().format(**configuration)
	html = load_html_template().format(**configuration)

	email_body_text = MIMEText(text, 'plain')
	email_body_html = MIMEBase('text', 'html')
	email_body_html.set_payload(html)
	encoders.encode_quopri(email_body_html)
	email_body_html.set_charset('UTF-8')

	email.attach(email_body_text)
	email.attach(email_body_html)

	email["DKIM-Signature"] = sign_email(email, configuration)

	context = ssl.create_default_context()
	for mx_record in dns.resolver.query(configuration['SSH_MAIL_USER_TODOMAIN'], 'MX'):
		mail_server = mx_record.to_text().split()[1][:-1]
		try:
			server = smtplib.SMTP(mail_server, local_hostname='obtain.life', port=25, timeout=10) # 587 = TLS, 465 = SSL

			if server.starttls(context=context)[0] != 220:
				log('Could not start TLS.', level=3, origin='mailer')
			
			server.sendmail('{SSH_MAIL_USER_FROM}@{SSH_MAIL_USER_FROMDOMAIN}'.format(**configuration), '{SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN}'.format(**configuration), email.as_string())
			server.quit()
		#		server.close()

			configuration['mail_server'] = mail_server
			log("Sent email from {SSH_MAIL_USER_FROM}@{SSH_MAIL_USER_FROMDOMAIN} to {SSH_MAIL_USER_TO}@{SSH_MAIL_USER_TODOMAIN} about via {mail_server}.".format(**configuration), level=4, origin='mailer')

			return True
		except Exception as e:
			log("Could not send email via: {}!!".format(mail_server), level=3, origin='mailer')
			log("{}".format(e), level=3, origin='mailer')

			if configuration['TRY_ONE_MAILSERVER']:
				break

	return False