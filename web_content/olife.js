function hexdigest(data) {
	return [...new Uint8Array(data)].map(b => b.toString(16).padStart(2, '0')).join('');
}

const getUtf8Bytes = str =>
	new Uint8Array(
	[...unescape(encodeURIComponent(str))].map(c => c.charCodeAt(0))
);

class _olife {
	constructor(domain, mode, secret) {
		this.domain = domain;
		this.mode = mode;
		this.key = secret;
	}

	sign(data, key, func) {
		let payload = getUtf8Bytes(JSON.stringify(data));
		crypto.subtle.importKey('raw', getUtf8Bytes(key), { name: 'HMAC', hash: 'SHA-256' }, true, ['sign']).then(function(cryptoKey) {
			crypto.subtle.sign('HMAC', cryptoKey, payload).then(function(signature) {
				func(hexdigest(signature));
			})
		})
	}

	subscribe(domain, secret, func=null) {
		let payload = {
			"alg": "HS256",
			"domain": domain,
			"_module": "register",
			"service": "backend"
		}
		this.sign(payload, secret, (service_signature) => {
			payload['service_sign'] = service_signature;
			this.sign(payload, this.key, (signature) => {
				payload['sign'] = signature;
				if(func)
					func(payload);
				else
					console.warn('No function given to subscribe.')
			})
		})
	}

	login(user, pass, func=null) {
		let payload = {
			"alg": this.mode,
			"domain": this.domain,
			"_module": "auth",
			"username": user,
			"password": pass
		}

		this.sign(payload, this.key, (signature) => {
			payload['sign'] = signature;
			if(func)
				func(payload);
			else
				console.warn('No function given to login.')
		})
	}
}

window.olife = _olife;
