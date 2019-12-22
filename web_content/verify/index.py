class parser():
	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		print('Verifying:', data)

		if not 'mode' in headers['GET']: return None
		if not 'domain' in headers['GET']: return None