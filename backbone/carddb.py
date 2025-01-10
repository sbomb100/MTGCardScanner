import sqlite3
import re

class CardDatabases:
    def __init__(self):
        self.my_cards = sqlite3.connect("./databases/MTGPersonalCollection.db")
        self.my_cursor = self.my_cards.cursor()
        self.db = sqlite3.connect("./databases/scryfall.db")
        self.cards_cursor = self.db.cursor()
    
    def close_db(self):
        self.my_cards.close()
        self.db.close()

    def search_card_by_name(self, name):
        self.cards_cursor.execute("""SELECT id, name, set_name, type, rarity, mana_cost, oracle_text, card_img
                        FROM cards WHERE name = ?""", (self.format_mtg_name(name),))
        card = self.cards_cursor.fetchone()
        if card is not None:
            self.cards_cursor.execute("""
                SELECT card_id, usd, usd_foil
                FROM prices
                WHERE card_id = ?
                """, (card[0],))

            price = self.cards_cursor.fetchone()
            return (*card[:8], price[1], price[2])
        
        return None
    
    def format_mtg_name(self, card_name):
        exceptions = {'and', 'or', 'the', 'a', 'an', 'in', 'of', 'to', 'for', 'with'}
        words = re.split('([ -])', card_name) 
        formatted_name = []

        for i, word in enumerate(words):
            if word in {' ', '-'}:
                formatted_name.append(word)
            else:
                if i == 0 or word not in exceptions:
                    formatted_name.append(word.capitalize())
                else:
                    formatted_name.append(word)
        
        return ''.join(formatted_name)