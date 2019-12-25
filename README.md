# obtain.life *(work in progress)*
A central authentication system *(Identity Manager)* for HTTP, WebSockets and socket requests.<br>
Basic principle is simple, resembles JWT's logic, is stripped down and easy to use.

![certs](https://img.shields.io/badge/dummy%20certs-not%20prodction-blue.svg)

# Integration libraries

 * [python-olife](https://github.com/Torxed/python-olife)
 * [javascript-olife](https://github.com/Torxed/javascript-olife)

# Struct?

The struct is a minified-version of JWT.<br>
It contains the same principle as JWT, but with a smaller footprint.

Instead of three seperate JSON payloads, concatinated with dots,<br>
obtain.life is a single JSON payload with a signature baked in before sending.

A basic example without any application data would look like this:

```json
	{
		"alg" : "HS256",
		"sign" : hmac.new(shared_key,msg=data_without_sign_key,digestmod=hashlib.sha256).hexdigest().upper()
	}
```

More info on this and other algorithms can be found in the [wiki](https://github.com/Torxed/obtain.life/wiki).

# How to login/register?

First, your or your orgnization needs to create a master account for your domain.<br>
This is so that someone can setup the auth-flow (callbacks etc).

This is done by going to https://obtain.life and "claim" your domain.<br>
The [claim](https://github.com/Torxed/obtain.life/wiki) works by checking against a DNS TXT record *(TXT record must be called `_obtain.life.[claimed domain]`)* or via HTTPS file lookup on [https://[claimed.domain]/obtain.life.txt](https://[claimed.domain]/obtain.life.txt). Once the claim is verified, the claim-ee will be prompted to enter a password for the new administrative account. If no password was given at the time, a reminder e-mail will be sent out and the administrator has 24h to complete the registration before the domain claim becomes void and discarded.

One administrative account can claim multiple domains and manage them individually.

Once the domain is claimed, back-end services can `subscribe` to events and users can login via sockets, websockets or HTTPS against the claimed domain. For more on the `subscribe` API, visit the documentation/wiki.

All credentials and supplied user-information is stored in the `obtain.life` database according to current industry standards *(Currently that means salted with a strong hash and protected by 2FA)*.<br>
But to ensure `obtain.life` can't access resources on your domains infrastructure *(by impersonating your users)*,<br>
add additional tokens/shared secrets to your own payloads when talking with your domain infrastructure. This ensures that `obtain.life` developers and maintainers can't hijack a session without heavily brute forcing the service tokens on your end *(not that we'll ever do this, but we'd like to help our users follow best practices)*

`obtain.life` simply provides a good compliant way to store credentials, and SSO possebility across domain resources.<br>

## Cross-domain support?

Yes, there's cross domain support. The domain admin(s) for each individual domain has to approve cross-domain token sharing in order for SSO to work across domains. Sub-domains are automatically eligible for this kind of service, but can be explicitly turned off by the domain administrator(s).
