# SQL Setup Guide — Patient Journey & Treatment Adoption Analytics

This guide explains how to load `data/patient_data_clean.csv` into a local SQL database
and run the business analysis queries in `sql/business_analysis.sql`.

---

## Option A — SQLite (Easiest, No Installation Required)

SQLite is built into Python. No server setup is needed.

### Step 1 — Import the CSV into SQLite

```python
import pandas as pd
import sqlite3

df = pd.read_csv("data/patient_data_clean.csv")

con = sqlite3.connect("patient_data.db")
df.to_sql("patient_data_clean", con, if_exists="replace", index=False)
con.close()

print("Database created: patient_data.db")
```

Save this as a script and run it from the project root:

```bash
python -c "
import pandas as pd, sqlite3
df = pd.read_csv('data/patient_data_clean.csv')
con = sqlite3.connect('patient_data.db')
df.to_sql('patient_data_clean', con, if_exists='replace', index=False)
con.close()
print('Done.')
"
```

### Step 2 — Run Queries

```python
import sqlite3, pandas as pd

con = sqlite3.connect("patient_data.db")

query = """
SELECT Region,
       COUNT(*) AS Total_Patients,
       ROUND(100.0 * SUM(Treatment_Started) / COUNT(*), 2) AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Region
ORDER BY Adoption_Rate_Pct DESC
"""

df = pd.read_sql_query(query, con)
print(df)
con.close()
```

You can copy-paste any query from `sql/business_analysis.sql` into the `query` variable.

---

## Option B — MySQL

### Prerequisites
- MySQL Server installed and running
- MySQL Connector for Python: `pip install mysql-connector-python`

### Step 1 — Create Database and Table

Connect to MySQL and run:

```sql
CREATE DATABASE IF NOT EXISTS patient_analytics;
USE patient_analytics;
```

### Step 2 — Import CSV Using Python

```python
import pandas as pd
import mysql.connector

df = pd.read_csv("data/patient_data_clean.csv")

# Replace with your actual credentials
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="patient_analytics"
)
cursor = conn.cursor()

# Create table
cursor.execute("DROP TABLE IF EXISTS patient_data_clean")
cursor.execute("""
CREATE TABLE patient_data_clean (
    Patient_ID            VARCHAR(10),
    Age                   INT,
    Gender                VARCHAR(20),
    Region                VARCHAR(20),
    State                 VARCHAR(30),
    Urban_Rural           VARCHAR(15),
    Income_Band           VARCHAR(10),
    Insurance_Status      VARCHAR(20),
    Disease_Severity      VARCHAR(10),
    Diagnosis_Date        DATE,
    Doctor_Consultation   INT,
    Treatment_Recommended INT,
    Treatment_Cost        INT,
    Affordability_Score   FLOAT,
    Healthcare_Access_Score FLOAT,
    Awareness_Score       FLOAT,
    Previous_Treatment    INT,
    Side_Effect_Concern   FLOAT,
    Treatment_Started     INT,
    Treatment_Start_Date  DATE,
    Treatment_Continued   INT,
    Follow_Up_Completed   INT,
    Drop_Off_Stage        VARCHAR(40),
    Age_Group             VARCHAR(10),
    Cost_Band             VARCHAR(25)
)
""")

# Insert rows
for _, row in df.iterrows():
    vals = [None if (str(v) == "nan" or str(v) == "NaT") else v
            for v in row.values]
    cursor.execute(
        "INSERT INTO patient_data_clean VALUES (%s," + "%s," * 24 + "%s)",
        vals[:25]   # 25 columns
    )

conn.commit()
cursor.close()
conn.close()
print("MySQL import complete.")
```

### Step 3 — Run Queries

Open MySQL Workbench or the MySQL command line, switch to `patient_analytics`, and
paste queries from `sql/business_analysis.sql`.

---

## Option C — PostgreSQL

### Prerequisites
- PostgreSQL Server installed and running
- psycopg2: `pip install psycopg2-binary`

### Step 1 — Create Database

```bash
createdb patient_analytics
```

### Step 2 — Import CSV Using Python

```python
import pandas as pd
import psycopg2
from psycopg2 import sql

df = pd.read_csv("data/patient_data_clean.csv")

# Replace with your credentials
conn = psycopg2.connect(
    host="localhost",
    dbname="patient_analytics",
    user="your_username",
    password="your_password"
)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS patient_data_clean")
cur.execute("""
CREATE TABLE patient_data_clean (
    Patient_ID              TEXT,
    Age                     INT,
    Gender                  TEXT,
    Region                  TEXT,
    State                   TEXT,
    Urban_Rural             TEXT,
    Income_Band             TEXT,
    Insurance_Status        TEXT,
    Disease_Severity        TEXT,
    Diagnosis_Date          DATE,
    Doctor_Consultation     INT,
    Treatment_Recommended   INT,
    Treatment_Cost          INT,
    Affordability_Score     FLOAT,
    Healthcare_Access_Score FLOAT,
    Awareness_Score         FLOAT,
    Previous_Treatment      INT,
    Side_Effect_Concern     FLOAT,
    Treatment_Started       INT,
    Treatment_Start_Date    DATE,
    Treatment_Continued     INT,
    Follow_Up_Completed     INT,
    Drop_Off_Stage          TEXT,
    Age_Group               TEXT,
    Cost_Band               TEXT
)
""")

for _, row in df.iterrows():
    vals = [None if str(v) in ("nan", "NaT", "None") else v for v in row.values]
    cur.execute(
        "INSERT INTO patient_data_clean VALUES (" + ",".join(["%s"] * 25) + ")",
        vals
    )

conn.commit()
cur.close()
conn.close()
print("PostgreSQL import complete.")
```

### Step 3 — Run Queries

Use psql, pgAdmin, or DBeaver to connect to `patient_analytics` and run
queries from `sql/business_analysis.sql`.

---

## Notes on SQL Compatibility

The queries in `sql/business_analysis.sql` are written to work with **SQLite**, **MySQL**,
and **PostgreSQL**. Minor syntax differences may exist:

| Feature           | SQLite            | MySQL             | PostgreSQL        |
|-------------------|-------------------|-------------------|-------------------|
| String functions  | `SUBSTR()`        | `SUBSTRING()`     | `SUBSTRING()`     |
| Date functions    | `SUBSTR(date,1,7)`| `DATE_FORMAT()`   | `TO_CHAR()`       |
| LIMIT             | `LIMIT n`         | `LIMIT n`         | `LIMIT n`         |
| Window functions  | Supported (3.25+) | Supported (8.0+)  | Fully supported   |

For most queries there is **no difference**. The monthly trend query (Query 13) uses
`SUBSTR()` which works in SQLite; adjust to `DATE_FORMAT()` (MySQL) or `TO_CHAR()`
(PostgreSQL) if needed.

---

*This project uses synthetic data for educational purposes only.*
