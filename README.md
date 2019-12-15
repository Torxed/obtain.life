# obtain.life
A central authentication system for WebSockets and Sockets

# Struct?

The struct is a minified-version of JWT.<br>
It contains the same principle as JWT, but with a smaller footprint.

Instead of three seperate JSON payloads, concatinated with a dot,<br>
miniJWT is a single delivered JSON payload with a signature baked in before sending.

More info at [miniJWT](https://github.com/Torxed/miniJWT).

# How to login/register?

First, your or your orgnization needs to create a master account for your domain.<br>
This is so that someone can setup the auth-flow (callbacks etc).

After that, simply connect via sockets, websockets or HTTPS and login witn your domain.<br>
obtrain.life will contact your backend and let your environment know what tokens are validated.

All credentials are stored in the obtain.life database as securely as possible.<br>
But to ensure obtain.life can't access resources on your infrastructure,<br>
add one additional token to your payloads, only known by your clients and your infrastructure.

This way, obtain.life can handle the authentication, and your trust in that obtain.life won't be able<br>
to access any data/information is ensured. We simply provide a good compliant way to store credentials.