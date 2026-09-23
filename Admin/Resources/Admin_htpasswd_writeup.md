# Admin (htpasswd) — Writeup

**Flag:** `d19b4823e0d5600ceed56d5e896ef328d7a2b9e7ac7e80f4fcdb9b10bcb3e7ff`

## Discovery method

1. `http://<IP>/robots.txt` contains `Disallow: /whatever`. This directive is meant to keep search engines out, but the file is readable by anyone, so in practice it points an attacker straight at what the developer wanted to hide.
2. `http://<IP>/whatever/` shows an open directory listing (the server did not disable indexing when no index file is present). It contains one file: `htpasswd`.
3. `http://<IP>/whatever/htpasswd` contains a single line in the standard `login:hash` format used for HTTP Basic Auth:

   ```
   root:437394baff5aa33daa618be47b75cb49
   ```

4. The hash is 32 hex characters — an unsalted MD5, which makes it easy to crack.

## Reproduction

1. Crack the MD5 hash → password `qwerty123@`. Verify by recomputing `MD5("qwerty123@")` locally and comparing byte-for-byte with the hash above.
2. The login form lives at a direct path, `http://<IP>/admin/`, with no link from the rest of the site ("security through obscurity").
3. Log in with `root` / `qwerty123@`. The server returns the flag.

## The problem

Several classic misconfigurations stacked together, each a vulnerability on its own:

- **Open directory listing** — the server exposes folder contents when no index file exists.
- **Credentials file served over HTTP** — files like `htpasswd` should live outside the web root or be blocked by server rules.
- **Weak hashing** — plain unsalted MD5 with a common password is cracked almost instantly.
- **"Hidden" admin page with no real protection** — `/admin/` requires no server-side auth; the only "defense" is the absence of a link, which is not a defense.
- **`robots.txt` as an information leak** — a file meant for crawlers hands the attacker a map of what to look at.

## Flag comparison

Flag obtained through exploitation (`/admin/` after logging in as `root`/`qwerty123@`):

```
d19b4823e0d5600ceed56d5e896ef328d7a2b9e7ac7e80f4fcdb9b10bcb3e7ff
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
