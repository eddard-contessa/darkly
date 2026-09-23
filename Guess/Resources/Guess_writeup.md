# Guess (hidden file) — Writeup

**Flag:** `d5eec3ec36cf80dce44a896f961c1831a05526ec215693c8f2c39543497d4466`

## Research logic

This is **information leakage through `robots.txt`** (security through obscurity). The developers listed the directories they wanted to hide from search engines in `robots.txt` — but that file is public, so instead of hiding those paths it reveals them.

```
GET /robots.txt
User-agent: *
Disallow: /whatever
Disallow: /.hidden
```

Both `Disallow` entries point straight at paths the admin wanted hidden.

## Reproduction

1. Open `/.hidden/` — the server shows an open directory listing (nginx autoindex). Inside are 26 folders (one per letter a–z) and a `README`.
2. Every subfolder repeats the same structure: 26 folders + a `README`. It is a procedurally generated maze of tens of thousands of directories.
3. Each `README` holds one of six joke lines in French (e.g. "Demande à ton voisin de droite", "Non ce n'est toujours pas bon ..."). Clicking through by hand is impossible.
4. A small Python script (standard library + `requests`, no exploit tools) crawls the directories recursively, downloads every `README`, and compares their contents by text to find the one that differs from the jokes. Script attached in `Resources/darkly_hidden_crawler.py`.
5. Of ~31,000 downloaded READMEs, six joke texts repeat 5000+ times each, while one text appears only twice:

   ```
   Hey, here is your flag : d5eec3ec36cf80dce44a896f961c1831a05526ec215693c8f2c39543497d4466
   ```

   Path:
   ```
   /.hidden/whtccjokayshttvxycsvykxcfm/igeemtxnvexvxezqwntmzjltkt/lmpanswobhwcozdqixbowvbrhw/README
   ```

## Benefit

Any file or directory left in the public web tree can be found and read by an outsider when the server serves it without an access check. Here the same `robots.txt` also exposed `/whatever/`, which held `htpasswd` (a login/password hash) — so one architectural mistake (publishing paths in `robots.txt` + open autoindex) leaks several kinds of sensitive data. In real systems open autoindex often exposes backups, config files and database dumps, so the real-world payoff is much larger than in this exercise.

## Flag comparison

Flag obtained through exploitation:

```
d5eec3ec36cf80dce44a896f961c1831a05526ec215693c8f2c39543497d4466
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense.
