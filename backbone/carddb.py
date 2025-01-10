import sqlite3

class CardDatabases:
    def __init__(self):
        self.my_cards = sqlite3.connect("./databases/MTGPersonalCollection.db")
        self.my_cursor = self.my_cards.cursor()
        self.db = sqlite3.connect("./databases/scryfall.db")
        self.cards_cursor = self.db.cursor()
    
    def close_db(self):
        self.connection.close()
        self.db.close()