import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("MTGPersonalCollection.db")
cursor = conn.cursor()

card_name = "Psychic Whorl"
# Check if "Static Orb" is in the 'cards' table
cursor.execute("SELECT id, name, set_name FROM cards WHERE name = ?", (card_name,))
card = cursor.fetchone()

if card:
    print(f"Found card: {card}")
else:
    print(f"Card '{card_name}' not found.")

# Check prices for "Static Orb"
cursor.execute("""
SELECT card_id, usd, usd_foil
FROM prices
WHERE card_id = (SELECT id FROM cards WHERE name = ?)
""", (card_name,))
price = cursor.fetchone()

if price:
    print(f"Prices for '{card_name}': {price}")
else:
    print(f"Price data for '{card_name}' not found.")

# Close the connection
conn.close()
