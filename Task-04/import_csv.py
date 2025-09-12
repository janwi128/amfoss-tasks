import mysql.connector
import pandas as pd
import math

host = "localhost"
user = "root"              
password = "janwi128"   
database = "cinescope_db"

try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL successfully!")
except mysql.connector.Error as e:
    print(f"❌ Error connecting to MySQL: {e}")
    exit()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
cursor.execute(f"USE {database}")

try:
    df = pd.read_csv("movies.csv")
    
    df.columns = df.columns.str.strip().str.lower()
    print(f"✅ Loaded CSV with {len(df)} rows and normalized column names.")
except FileNotFoundError:
    print("❌ movies.csv not found in the current folder.")
    exit()


cursor.execute("DROP TABLE IF EXISTS movies")
cursor.execute("""
CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    series_title VARCHAR(255),
    released_year INT,
    genre VARCHAR(100),
    imdb_rating FLOAT,
    director VARCHAR(255),
    star1 VARCHAR(255),
    star2 VARCHAR(255),
    star3 VARCHAR(255)
)
""")
print("✅ Table 'movies' created successfully.")


for _, row in df.iterrows():
    
    released_year = int(row['released_year']) if not math.isnan(row['released_year']) else None
    imdb_rating = float(row['imdb_rating']) if not math.isnan(row['imdb_rating']) else None

    cursor.execute("""
        INSERT INTO movies (series_title, released_year, genre, imdb_rating, director, star1, star2, star3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['series_title'],
        released_year,
        row['genre'],
        imdb_rating,
        row['director'],
        row['star1'],
        row['star2'],
        row['star3']
    ))


conn.commit()
cursor.close()
conn.close()

print("✅ CSV data imported successfully into MySQL!")

