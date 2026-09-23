# Redirect — Writeup

**Flag:** `b9e775a0291fed784a2d9680fcfad7edd6b8cdf87648da647aaf4bba288bcab3`

## Mechanism

The site offers social-media links through the route:

```
index.php?page=redirect&site=<name>
```

The Facebook / Twitter / Instagram footer icons use this route with `site` set to `facebook`, `twitter` or `instagram`. The backend takes `site` **without any whitelist check** and uses it as the redirect target (`Location` header).

This is a classic **Open Redirect**: the link visibly starts with the trusted Darkly domain but sends the user wherever the `site` parameter points.

## Reproduction

```
?page=redirect&site=facebook          -> 302 Moved Temporarily, redirects to real facebook.com
?page=redirect&site=https://example.com  -> 200, flag printed in the HTML
```

A known value produces a real redirect; any value outside the expected set is handled differently and returns the flag directly in the page, confirming the parameter is not restricted to a fixed set of domains.

## Flag comparison

Flag obtained through exploitation (unexpected `site` value):

```
b9e775a0291fed784a2d9680fcfad7edd6b8cdf87648da647aaf4bba288bcab3
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
