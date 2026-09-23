# Cookies — Writeup

**Page:** `?page=admin` (a route inside `index.php`, not the physical `/admin/` directory).
**Flag:** `df2eb4ba34ed059a1e3e89ff4dfc13445f104a1a52295214def1c4fb1693a5c3`

## Mechanism

The `?page=admin` route decides whether you are an admin from the value of a **cookie** (`I_am_admin`), which is stored and fully controlled on the client.

The initial cookie value is:

```
68934a3e9455fa72420237eb05902327
```

That is `MD5("false")`. The server compares the incoming cookie against precomputed `MD5("true")` / `MD5("false")` to show or hide admin content. Since the algorithm is public (MD5) and the input set is tiny and predictable (`true`/`false`), anyone can compute `MD5("true")` and set it themselves. The cookie is never signed or bound to a server-side session, so the server has no way to tell a forged value from a real one.

## Reproduction

1. Open `http://127.0.0.1:8080/?page=admin` — it returns 200 but shows a JS `alert("Wtf ?")` instead of content.
2. DevTools → Application → Cookies → find `I_am_admin` = `68934a3e9455fa72420237eb05902327`.
3. Compute `MD5("true")` = `b326b5062b2f0e69046810717534cb09`.
4. Replace the cookie value with `b326b5062b2f0e69046810717534cb09`.
5. Reload — the alert is gone and the flag is shown.

## Fix

- Do not store access rights on the client in a plain or easily computed form. Rights should be checked server-side via a session ID tied to server-stored session data.
- If state must live in a cookie, use a signed or encrypted token (HMAC-SHA256 with a secret server key, or a JWT with signature verification), so the client cannot forge it even knowing the algorithm.
- Do not use MD5 for authentication/integrity — it is fast and collision-prone; use HMAC with a secret key.
- Set `HttpOnly` (and `Secure` where relevant) on such cookies to reduce theft via XSS.

## Impact

Any user with no credentials gets full access to the admin functionality just by editing one cookie — a complete bypass of authentication and authorization (Broken Access Control). In a real app this could mean access to the control panel, other users' data, content changes, user deletion, and so on. The root cause is a trust boundary violation: the server trusts data the client fully controls.

## Flag comparison

Flag obtained through exploitation:

```
df2eb4ba34ed059a1e3e89ff4dfc13445f104a1a52295214def1c4fb1693a5c3
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
