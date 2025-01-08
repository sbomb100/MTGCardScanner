import sqlite3
import os
import sys

#how expensive does a card have to be to warrant a proxy
#somewher ebetween 1 - 2 USD
PROXY_LIMIT = 1.25

#CONSIDER changing output in file to be easier to paste into proxy websites

method = (input("Command-Line (cl) or Text File (txt)?\n")).lower()
connection = sqlite3.connect("./databases/MTGPersonalCollection.db")
cursor = connection.cursor()
db = sqlite3.connect("./databases/cards.db")
cards_cursor = db.cursor()

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
out_filename = "filler"
owned_cards = []
cheap_needed_cards = []
proxy_needed_cards = []
unable_to_buy = []

def sort_cards(line, name):
            cursor.execute("SELECT id, name, count FROM cards WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result != None:
                owned_cards.append(result)
            else: #check scryfall
                cards_cursor.execute("""
                SELECT card_id, usd, usd_foil
                FROM prices
                WHERE card_id = (SELECT id FROM cards WHERE name = ?)
                """, (name,))
                queried_card = cards_cursor.fetchone()
                if queried_card != None:
                    if (queried_card == None):
                        print("err- no price")
                        return
                    #no price
                    if (queried_card[1] == None and queried_card[2] == None):
                        unable_to_buy.append(line)
                    else:
                        if  round(float(queried_card[(1 if queried_card[1] != None else 2)]), 2) < PROXY_LIMIT:
                            cheap_needed_cards.append(line)
                        else:
                            proxy_needed_cards.append(line)
                else:
                    print("error- card not found on scryfall")

if (method == "txt" or method == "text"):
    print("\nReading Text File -----")
    filename = ensure_txt_extension(input("Type Text File Name\n")) 

    with open(filename, 'r') as file:
        #get commander name:
        commander_name = file.readline().split(" (")[0]
        if (commander_name == ""):
            out_filename = get_unique_filename()
        else:
            out_filename = f"{commander_name.replace(" ", "_").lower()}.txt"

        #write whole deck into 2 lists of owned and unowned for better writing into file
        file.seek(0)
        for line in file:
            sort_cards(line, line.split(" (")[0])
                

#read through command line
elif (method == "cl" or method == "commandline" or method == "command-line"):
    print("\nPaste List:")
    list = sys.stdin.read()
    lines = list.strip().split("\n")
    commander_name = lines[0].split(" (")[0]
    if (commander_name == ""):
        out_filename = get_unique_filename()
    else:
        out_filename = f"{commander_name.replace(" ", "_").lower()}.txt"

    for line in lines:
        print(line.split(" (")[0])
        sort_cards(line, line.split(" (")[0])

else: 
    print("invalid input")

#write to file
with open(out_filename, 'w') as outfile:
    outfile.write("OWNED CARDS -----------------\n")
    for item in owned_cards:
        outfile.write(f"You have {item[2]} of {item[1]}\n")
    
    outfile.write("\nCHEAP UNOWNED CARDS -----------------\n")
    for item in cheap_needed_cards:
        outfile.write(f"{item}")
        if not item.endswith("\n"):
            outfile.write("\n")

    outfile.write("\nPROXY UNOWNED CARDS -----------------\n")
    for item in proxy_needed_cards:
        outfile.write(f"{item}")
        if not item.endswith("\n"):
            outfile.write("\n")

    outfile.write("\nUNPRICED CARDS -----------------\n")
    for item in unable_to_buy:
        outfile.write(f"{item}")
        if not item.endswith("\n"):
            outfile.write("\n")



connection.close()
db.close()

print("-- DONE -- \n")