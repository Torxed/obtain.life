
def response(root, path, payload, headers, *args, **kwargs):
	if not b'mode' in headers[b'path_payload']: return None
	if not b'domain' in headers[b'path_payload']: return None

	mode = headers[b'path_payload'][b'mode'].decode('UTF-8')
	domain = headers[b'path_payload'][b'domain'].decode('UTF-8')

	log(f'Starting verification for domain {domain} via {mode}', level=4, origin='verify')
	return {}, b'Ain\'t got nothing.'