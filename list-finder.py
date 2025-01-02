import sqlite3
import os
import sys

method = (input("Command-Line (cl) or Text File (txt)?\n")).lower()
connection = sqlite3.connect("MTGPersonalCollection.db")
cursor = connection.cursor()
db = sqlite3.connect("cards.db")
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

if (method == "txt" or method == "text"):
    print("Reading Text File\n")
    filename = ensure_txt_extension(input("Type Text File Name\n")) 
    print("-----------------------------\n")   
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
            cursor.execute("SELECT id, name, count FROM cards WHERE name = ?", (line.split(" (")[0],))
            result = cursor.fetchone()
            if result:
                owned_cards.append(result)
            else:
                cards_cursor.execute("SELECT id FROM cards WHERE name = ?", (line.split(" (")[0],))
                queried_card = cards_cursor.fetchone()
                print(queried_card)
                if queried_card:
                    cards_cursor.execute("SELECT card_id, usd, usd_foil FROM prices WHERE card_id = ?", (queried_card[0],))
                    price_card = cards_cursor.fetchone()
                    print(price_card)
                    #cheap_needed_cards.append(result) if  round(float(price_card[1]), 2) < 1.25 else proxy_needed_cards.append(result)
                else:
                    print("error")
                

#read through command line
elif (method == "cl" or method == "commandline" or method == "command-line"):
    print("Paste List:\n")
    list = sys.stdin.read()
    lines = list.strip().split("\n")
    print("-----------------------------\n")
    for line in lines:
        cursor.execute("SELECT 1 FROM cards WHERE name = ?", (line.split(" (")[0],))
        result = cursor.fetchone()
        if result:
            print(f"{line.split(" (")[0]} exists in the database!")
        else:
            print(f"{line.split(" (")[0]} does NOT exist in the database!")

else: 
    print("invalid input")

#write to file
with open(out_filename, 'w') as outfile:
    outfile.write("OWNED CARDS -----------------\n")
    for item in owned_cards:
        outfile.write(f"You have {item[1]} of {item[0]}\n")
    
    outfile.write("CHEAP UNOWNED CARDS -----------------\n")
    for item in cheap_needed_cards:
        outfile.write(f"{item[0]}\n")

    outfile.write("PROXY UNOWNED CARDS -----------------\n")
    for item in proxy_needed_cards:
        outfile.write(f"{item[0]}\n")

print("-- DONE -- \n")