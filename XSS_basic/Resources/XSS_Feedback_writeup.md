# XSS Basic — Feedback page — Writeup

**Page:** `?page=feedback` (form "Sign Guestbook") — fields `txtName` (Name) and `mtxtMessage` (Message).
**Flag:** `0fbb54bbf7d099713ca4be297e1bc7da0173d8b3c21c1811b916a3a86652724e`

## Mechanism

The `txtName` field gets no server-side sanitization: whatever is submitted is written into the HTML response verbatim, without escaping `<`, `>`, `'`, `"`. Since guestbook entries are stored and shown to every visitor, this is a **persistent (stored) XSS** — an injected payload runs for everyone who opens the page.

The `Message` field, by contrast, is filtered by a `strip_tags()`-style function (no allowed-list): any `<...>` sequence is removed, so `Message` is not a usable vector. The whole vulnerability lives in the `Name` field.

## Reproduction

1. In DevTools, raise the `maxlength` of the Name field (the 10-char limit is frontend-only and does nothing on the server).
2. Confirm arbitrary HTML/JS execution via Name: payloads such as `<svg onload=alert(1)>` and `<Script>alert(42)</Script>` are reflected into the HTML as-is and run in the browser of anyone who opens the page.
3. The flag itself is emitted by a separate server-side text check: if the submitted `Name` contains the substring `script`, the server prints the flag directly in the HTML. Submitting `txtName=script` (with any non-empty Message, since both fields are required) returns the flag.

Confirmed the same behaviour via `curl` (no browser), proving the filtering is server-side, not client JS validation.

## Flag comparison

Flag obtained through exploitation:

```
0fbb54bbf7d099713ca4be297e1bc7da0173d8b3c21c1811b916a3a86652724e
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
