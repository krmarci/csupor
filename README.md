# csupor

Flask-based login and personnel data management system backed by MySQL schema `csupor`.

## Features

- Login using **e-mail or username + password**.
- Registration using **e-mail, username, password**.
- User privilege enum: `employee`, `hr`, `ceo`, `developer`.
- Numeric ascending user ID using MySQL auto-increment primary key.
- Additional personnel profile data after registration.
- Dependents management.
- Educational qualifications management (multiple records supported).
- Optional teacher professional exam record.


## SQL schema file

An explicit MySQL schema script is available at `sql/schema.sql`.
You can run it directly, for example:

```bash
mysql -u root -p < sql/schema.sql
```

## Setup

1. Create database schema:
   ```sql
   CREATE DATABASE csupor;
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   # edit values as needed
   export $(cat .env | xargs)
   ```
4. Run app:
   ```bash
   python run.py
   ```

Tables are created automatically on startup.
