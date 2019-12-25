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
		this.token = localStorage.getItem('obtain.life.token');
	}

	sign(data, key, func=null) {
		// If no key is given, assume that key contains the func
		// and we do key -> func, and insert this.key into key.
		if(typeof key !== 'string') {
			func = key
			key = this.key;
		}
		const unsigned_payload = Object.assign({}, data);
		console.log('Signing payload:', unsigned_payload);
		console.log('With key:', key)
		let payload = getUtf8Bytes(JSON.stringify(unsigned_payload));
		crypto.subtle.importKey('raw', getUtf8Bytes(key), { name: 'HMAC', hash: 'SHA-256' }, true, ['sign']).then(function(cryptoKey) {
			crypto.subtle.sign('HMAC', cryptoKey, payload).then(function(signature) {
				func(hexdigest(signature));
			})
		})
	}

	set_token(token) {
		this.token = token;
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

	claim(domain, email, func=null) {
		let payload = {
			"alg": this.mode,
			"_module": "claim",
			"domain": this.domain,
			"claim": domain,
			"admin": email
		}

		this.sign(payload, this.key, (signature) => {
			payload['sign'] = signature;
			if(func)
				func(payload);
			else
				console.warn('No function given to claim.')
		})
	}

	get_profile(userid=null, token=null, func=null) {
		if(!token) {
			console.warn('No token given to get_profile, can\'t request a profile without it.');
			return;
		}

		let payload = {
			"alg": this.mode,
			"_module": "profile",
			"token" : token,
			"domain": this.domain
		}

		console.log('Signing with key:', this.key);
		this.sign(payload, this.key, (signature) => {
			payload['sign'] = signature;
			if(func)
				func(payload);
			else
				console.warn('No function given to claim.')
		})
	}
}

window.olife = _olife;
