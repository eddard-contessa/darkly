# XSS Advanced — Writeup

**Page:** `?page=media&src=...`
**Flag:** `928d819fc19405ae09921a2b71227bd9aba106f9d2d37ac412e9e5a750f1506d`

## Mechanism

The `media` page displays an image inside an `<object>` tag:

```html
<object data="http://10.0.2.15/images/nsa_prism.jpg"></object>
```

If `src` matches a known name (e.g. `nsa`), it shows the built-in image. If not, the server drops into a fallback branch and inserts the raw `src` value directly into the `data="..."` attribute, without checking what it is.

The browser reads `data` as a URL and renders it based on its **scheme** (`http://`, `data:`, etc.). The only filtering the server does is stripping the substring `http://` (case-insensitive, single pass). That blocks the obvious remote HTTP inclusion but nothing else. The `data:` scheme lets us embed a whole HTML document (with a script) inside the URL itself:

```
data:text/html;base64,<Base64 HTML/JS>
```

The browser renders that HTML inside `<object>`, executing our code in the page's context — a **XSS via injection into the `<object data>` attribute**.

## Reproduction

```
?page=media&src=data:text/html;base64,PHNjcmlwdD5hbGVydChkb2N1bWVudC5jb29raWUpPC9zY3JpcHQ+
```

The Base64 decodes to `<script>alert(document.cookie)</script>`. The server detects the payload and prints the flag directly in the HTML.

If a raw `http://` were needed, the single-pass filter is bypassed by nesting it inside itself: `htthttp://p://` → after one removal becomes `http://`.

## Flag comparison

Flag obtained through exploitation:

```
928d819fc19405ae09921a2b71227bd9aba106f9d2d37ac412e9e5a750f1506d
```

Note: the page shows the flag in uppercase due to CSS `text-transform: uppercase`. The real value in the HTML source (View Page Source, Ctrl+U) is lowercase, as above — use that value when comparing with the `flag` file during the defense.
