# obtain.life
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

More info in the [wiki](https://github.com/Torxed/obtain.life/wiki).

# How to login/register?

First, your or your orgnization needs to create a master account for your domain.<br>
This is so that someone can setup the auth-flow (callbacks etc).

This is done by going to https://obtain.life and "claim" your domain.<br>
The claim works by checking against a DNS record *(TXT _obtain.life.[claimed domain])* or via HTTPS file lookup on https://[claimed.domain]/obtain.life. Once the claim is verified, the claim-ee will recieve a e-mail with a reset-password link to complete the master account for the domain. If multiple domains are claimed, only one password-email will go out and the same account can be used to manage multiple domains.

Once the domain is claimed, simply connect via sockets, websockets or HTTPS and login against your domain.<br>
`obtrain.life` will contact any backend's registered via the `register` API and let your environment know when tokens are distributed upon successful logins.

All credentials and supplied user-information is stored in the `obtain.life` database according to current industry standards.<br>
But to ensure `obtain.life` can't access resources on your infrastructure *(by impersonating your user)*,<br>
add one additional token/shared secret to your own payloads, only known by your clients and your infrastructure. This ensures that `obtain.life` personell can never hijack a session without heavily brute forcing the services *(not that we'll ever do this, but we'd like to help secure your services)*

`obtain.life` simply provides a good compliant way to store credentials, and SSO possebility.

## Cross-domain support?

Yes, there's cross domain support. The domain admin(s) for each individual domain has to approve cross-domain token sharing in order for SSO to work across domains. Sub-domains are automatically eligible for this kind of service, but can be explicitly turned off by the domain administrator(s).
