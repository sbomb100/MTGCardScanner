
import os
#how expensive does a card have to be to warrant a proxy
#somewher ebetween 1 - 2 USD


#CONSIDER changing output in file to be easier to paste into proxy websites
class DeckFinder:
    def __init__(self, money_limit, db):
        self.cursor = db.my_cursor()
        self.cards_cursor = db.cards_cursor()
        self.out_filename = "output"
        self.owned_cards = []
        self.cheap_needed_cards = []
        self.proxy_needed_cards = []
        self.unable_to_buy = []
        self.proxy_limit = money_limit

    
    def get_unique_filename():
    
        file_number = 1
        filename = f"magic_deck_{file_number}.txt"
        while os.path.exists(filename):
            file_number += 1
            filename = f"magic_deck__{file_number}.txt"
        
        return filename


    def ensure_txt_extension(filename):
        if os.path.splitext(filename)[1] == "":
            return f"{filename}.txt"
        elif not filename.endswith(".txt"):
            return f"{os.path.splitext(filename)[0]}.txt"
        return filename

    #read text file
    def search_name(self, name):
        self.cards_cursor.execute("""SELECT id, name, set_name, type, rarity, mana_cost, oracle_text, card_img
                        FROM cards WHERE name = ?""", (name,))
        return self.cards_cursor.fetchone()
            

    def sort_cards(self, line, name):
                self.cursor.execute("SELECT id, name, count FROM cards WHERE name = ?", (name,))
                result = self.cursor.fetchone()
                if result != None:
                    self.owned_cards.append(result)
                else: #check scryfall
                    self.cards_cursor.execute("""
                    SELECT card_id, usd, usd_foil
                    FROM prices
                    WHERE card_id = (SELECT id FROM cards WHERE name = ?)
                    """, (name,))
                    queried_card = self.cards_cursor.fetchone()
                    if queried_card != None:
                        if (queried_card == None):
                            print("err- no price")
                            return
                        #no price
                        if (queried_card[1] == None and queried_card[2] == None):
                            self.unable_to_buy.append(line)
                        else:
                            if  round(float(queried_card[(1 if queried_card[1] != None else 2)]), 2) < self.proxy_limit:
                                self.cheap_needed_cards.append(line)
                            else:
                                self.proxy_needed_cards.append(line)
                    else:
                        print("error- card not found on scryfall")
                        
    def get_output(self, method, data):
        if (method == "text"):
            filename = self.ensure_txt_extension(data) 

            with open(filename, 'r') as file:
                #get commander name:
                commander_name = file.readline().split(" (")[0]
                if (commander_name == ""):
                    out_filename = self.get_unique_filename()
                else:
                    out_filename = f"{commander_name.replace(" ", "_").lower()}.txt"

                #write whole deck into 2 lists of owned and unowned for better writing into file
                file.seek(0)
                for line in file:
                    self.sort_cards(line, line.split(" (")[0])
                        

        #read through command line
        elif (method == "paste"):
            lines = data.strip().split("\n")
            commander_name = lines[0].split(" (")[0]
            if (commander_name == ""):
                self.out_filename = self.get_unique_filename()
            else:
               self.out_filename = f"{commander_name.replace(" ", "_").lower()}.txt"

            output = ""
            for line in lines:
                output = output + (line.split(" (")[0])
                self.sort_cards(line, line.split(" (")[0])

        else: 
            self.output = ("invalid input")

    def write_output_to_file(self):
        #write to file
        with open(self.out_filename, 'w') as outfile:
            outfile.write("OWNED CARDS -----------------\n")
            for item in self.owned_cards:
                outfile.write(f"You have {item[2]} of {item[1]}\n")
            
            outfile.write("\nCHEAP UNOWNED CARDS -----------------\n")
            for item in self.cheap_needed_cards:
                outfile.write(f"{item}")
                if not item.endswith("\n"):
                    outfile.write("\n")

            outfile.write("\nPROXY UNOWNED CARDS -----------------\n")
            for item in self.proxy_needed_cards:
                outfile.write(f"{item}")
                if not item.endswith("\n"):
                    outfile.write("\n")

            outfile.write("\nUNPRICED CARDS -----------------\n")
            for item in self.unable_to_buy:
                outfile.write(f"{item}")
                if not item.endswith("\n"):
                    outfile.write("\n")


    
