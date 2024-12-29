import json
import sqlite3

# Load the JSON file
with open("../cards.json", "r", encoding="utf-8") as file:
    card_data = json.load(file)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("cards.db")
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
    oracle_text TEXT
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

# Insert data into tables
for card in card_data:
    # Use the 'id' field from the JSON as the primary key for the card
    
    cursor.execute("""
    INSERT INTO cards (id, name, set_name, type, rarity, mana_cost, oracle_text)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        card.get("id"),  # Use the 'id' (UUID) from the JSON
        card.get("name"),
        card.get("set"),
        card.get("type"),
        card.get("rarity"),
        card.get("mana_cost"),
        card.get("oracle_text")
    ))
    
    # Insert prices if available
    prices = card.get("prices", {})
    cursor.execute("""
    INSERT INTO prices (card_id, usd, usd_foil)
    VALUES (?, ?, ?)
    """, (
        card.get("id"),  # Use the 'id' to link to the card
        prices.get("usd"),
        prices.get("usd_foil")
    ))

# Commit and close
conn.commit()
conn.close()

print("Database successfully created!")
