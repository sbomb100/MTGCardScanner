
import sqlite3

conn = sqlite3.connect("./databases/MTGPersonalCollection.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY, 
    name TEXT NOT NULL,
    set_name TEXT,
    type TEXT,
    rarity TEXT,
    mana_cost TEXT,
    oracle_text TEXT,
    card_img TEXT,
    count INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER,
    usd TEXT,
    usd_foil TEXT,
    FOREIGN KEY (card_id) REFERENCES cards (id)
)
""")


conn.commit()
conn.close()

print("Database successfully created!")