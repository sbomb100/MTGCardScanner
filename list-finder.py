import sqlite3
import os
import sys

method = (input("Command-Line (cl) or Text File (txt)?\n")).lower()
connection = sqlite3.connect("MTGPersonalCollection.db")
cursor = connection.cursor()

def ensure_txt_extension(filename):
    if os.path.splitext(filename)[1] == "":
        return f"{filename}.txt"
    elif not filename.endswith(".txt"):
        return f"{os.path.splitext(filename)[0]}.txt"
    return filename

#read text file
if (method == "txt" or method == "text"):
    print("Reading Text File\n")
    filename = ensure_txt_extension(input("Type Text File Name\n")) 
    print("-----------------------------\n")   
    with open(filename, 'r') as file:
        for line in file:
            cursor.execute("SELECT 1 FROM cards WHERE name = ?", (line.split(" (")[0],))
            result = cursor.fetchone()
            if result:
                print(f"{line.split(" (")[0]} exists in the database!")
            else:
                print(f"{line.split(" (")[0]} does NOT exist in the database!")

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

print("-- DONE -- \n")