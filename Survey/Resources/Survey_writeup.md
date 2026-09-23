# Survey — Writeup

**Page:** `index.php?page=survey` (voting form, method POST).
**Flag:** `03a944b434d5baff05f46c4bede5792551a2595574bcafc9a6e25f67c382ccaa`

## Discovery technique

The form has two parameters:

- `sujet` — hidden field, the subject id (2–6 in the interface);
- `valeur` — a `<select>` offering values **1–10**, auto-submitted on change (`onChange`).

The `<select>` only *visually* limits the choice to 1–10. That is a browser-side restriction — nothing stops us from sending a POST request directly (curl) with any `valeur`. Testing the range showed the server does not actually enforce 1–10:

- `valeur` 0–10 → processed as a normal vote (average and vote count update);
- `valeur` > 10 (11, 15, 100, …) → the server treats it as an unexpected value and prints the flag instead of counting the vote;
- non-numeric/compound values (`5'`, `5 or 1=1`, `valeur[]=5`, missing param) → silently rejected, no flag, no SQL error;
- `sujet` is forced to an integer server-side (`intval()`-style), so no SQL injection through it.

This is **improper input validation** — the server trusts that the value is limited by the HTML `<select>` and never rechecks it.

## Reproduction

```bash
curl -s "http://127.0.0.1:8080/index.php?page=survey" --data "sujet=2&valeur=100"
```

Minimal working payload — any existing `sujet` (2–6) and any `valeur` strictly greater than 10:

```bash
curl -s "http://127.0.0.1:8080/index.php?page=survey" --data "sujet=3&valeur=11"
```

## Impact

Here the direct effect is skewing public voting statistics — an integrity issue more than a direct breach. But the same class of flaw (server trusting an HTML-limited value without rechecking) can be far worse in other contexts: tampering with a product price or quantity in an order, bypassing business limits (attempt counts, discount size), or DoS by feeding extreme values into calculations.

## Flag comparison

Flag obtained through exploitation:

```
03a944b434d5baff05f46c4bede5792551a2595574bcafc9a6e25f67c382ccaa
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
