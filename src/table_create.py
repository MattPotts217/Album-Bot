import sqlite3

conn = sqlite3.connect("./db/albums.db")
cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS albums (
                album_id INTEGER PRIMARY KEY AUTOINCREMENT,
                spotify_id TEXT UNIQUE,
                name TEXT NOT NULL,
                artist TEXT NOT NULL,
                art_url TEXT,
                release_date TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
               
               
               ''')

conn.commit()