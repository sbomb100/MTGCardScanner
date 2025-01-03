#used for images
import cv2
#used for matrix and perspective transformations
import numpy as np
#used to read the card texts
import pytesseract

import re
import sqlite3

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CAMERA_TO_USE = 1
last_card = ""

# Create a window
cv2.namedWindow("Trackbars")

def nothing(x):
    pass
# Create two trackbars to control the Canny edge detection thresholds
cv2.createTrackbar("Threshold1", "Trackbars", 50, 255, nothing)
cv2.createTrackbar("Threshold2", "Trackbars", 150, 255, nothing)

all_cards = sqlite3.connect("cards.db")
my_cards = sqlite3.connect("MTGPersonalCollection.db")

all_cursor = all_cards.cursor()
my_cursor = my_cards.cursor()



def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #weak and strong edge threshholds, gotten from parameter window
    threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    
    imgCanny = cv2.Canny(blurred, threshold1, threshold2)
 
    kernel = np.ones((5, 5), np.uint8)
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
   
    #makes list of shapes in the image in a hierarchy  
    #cv2.RETR_EXTERNAL - outermost shapes
    #cv2.CHAIN_APPROX_SIMPLE - remove redundant straight lines
    contours, _ = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest rectangular
        largest_contour = max(contours, key=cv2.contourArea)
        approx = cv2.approxPolyDP(largest_contour, 0.02 * cv2.arcLength(largest_contour, True), True)
        
        # Ensure it's a quadrilateral
        if len(approx) == 4:
            return approx  # Return the card contour
    
    return None

#initial bug: points will show up in contour array out of order. order them
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left
    rect[2] = pts[np.argmax(s)]  # Bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left

    return rect

def warp_card(img, contours):
    # Reshape the contour to a 4x2 format
    pts = contours.reshape(4, 2)

    # make sure points are ordered
    ordered_pts = order_points(pts)
    (tl, tr, br, bl) = ordered_pts

    # _ is the max length of the one side or the other (w= bottom vs top)
    width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

    #the array of points that we want to warp to
    target = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(ordered_pts, target)
    warped = cv2.warpPerspective(img, matrix, (width, height))

    return warped

#get the title from the card
def extract_card(img):
    
    # Ensure the card is in portrait orientation
    height, width = img.shape[:2]
    if width > height:  # Landscape orientation
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    # Dynamically calculate ROI based on card dimensions
    roi_x = int(0.07 * img.shape[1])  # 8% from the left
    roi_y = int(0.05 * img.shape[0])  # 5% from the top
    roi_w = int(0.60 * img.shape[1])  # 85% width
    roi_h = int(0.06 * img.shape[0])  # 15% height

    # Crop the ROI from the warped card image
    card_name_roi = img[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    cv2.imshow("name", card_name_roi)
    # Convert to grayscale for better OCR results
    gray_roi = cv2.cvtColor(card_name_roi, cv2.COLOR_BGR2GRAY)
    
    # Optional: Apply thresholding to enhance text visibility
    _, thresh_roi = cv2.threshold(gray_roi, 128, 255, cv2.THRESH_BINARY)
    cv2.imshow("Processed ROI", thresh_roi)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(thresh_roi)
    cv2.imshow("Contrast Enhanced", contrast_enhanced)
    # Perform OCR on the cropped ROI
    card_name = re.sub('[^a-zA-Z0-9,+ ]', '', pytesseract.image_to_string(thresh_roi)).strip()
    
    return card_name



#check the scryfall databse for the card via name
def update_database(card_data):
    global last_card

    all_cursor.execute("""SELECT id, name, set_name, type, rarity, mana_cost, oracle_text
                    FROM cards WHERE name = ?""", (card_data,))
    card = all_cursor.fetchone()
    if card:
        last_card = card_data.strip()
        print(f"Found card: {card}")
        #fetch the price
        all_cursor.execute("""
        SELECT card_id, usd, usd_foil
        FROM prices
        WHERE card_id = (SELECT id FROM cards WHERE name = ?)
        """, (card_data,))

        price = all_cursor.fetchone()

        if price:
            print(f"Prices for '{card_data}': {price}")
            
            my_cursor.execute("SELECT count FROM cards WHERE id = ?", (card[0],))
            existing_card = my_cursor.fetchone()
            #fetch the price
            if (existing_card):
                new_count = existing_card[0] + 1  # Add the new count to the existing one
                print(f"more cards, now at: {existing_card} of {card_data}!")
                my_cursor.execute("""
                UPDATE cards
                SET count = ?
                WHERE id = ?
                """, (new_count, card[0]))
                my_cards.commit()
            else:
                # If the card does not exist, insert a new card with count
                print("new card!\n")
                my_cursor.execute("""
                INSERT INTO cards (id, name, set_name, type, rarity, mana_cost, oracle_text, count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    card[0],
                    card[1],
                    card[2],
                    card[3],
                    card[4],
                    card[5],
                    card[6],
                    1
                ))

                my_cursor.execute("""
                INSERT INTO prices (card_id, usd, usd_foil)
                VALUES (?, ?, ?)
                """, (
                    price[0],  # Use the 'id' to link to the card
                    price[1],
                    price[2]
                ))
                print(f"Card Added -- {card[1]}")
                my_cards.commit()
        else:
            print(f"Card not found")

    

#open camera
cap = cv2.VideoCapture(CAMERA_TO_USE)
frame_count = 0
process_every_n_frames = 30

while True:
    #frame capture
    success, img = cap.read()
    cv2.imshow("Camera Feed", img)
    if not success:
        print("ERROR: Camera Broke")
        break
    #img = cv2.imread("../card-pics/treecity.jpg")
    #img = cv2.resize(img, None, fx=0.3, fy=0.3)
    #get the large edges
    card_contour = preprocess_image(img)
        
    frame_count += 1
    if card_contour is not None and frame_count % process_every_n_frames == 0:
        wrapped_card = warp_card(img, card_contour)
        card_data = extract_card(wrapped_card)
        
        
        #cv2.imshow("Contours", cv2.drawContours(resized_image.copy(), [card_contour], -1, (0, 255, 0), 2))
        #card_data = "The Beamtown Bullies"
        cv2.imshow("Warped", wrapped_card)
        #print(f"{card_data} is {last_card} \n")
        if card_data.strip() == "":
            #print("DEBUG: Card data is empty, skipping frame.")
            continue

        if card_data.strip() == last_card:
            print("DEBUG: Duplicate card detected, skipping database update.")
            continue
        else: 
            #now that we have the name, check databse
            
            ret = update_database(card_data)
       
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting")
        break

#cap.release()
all_cards.close()
my_cards.close()
cv2.destroyAllWindows()


#TODO:
#make so any orientation will get flipped upright.
#double check the card reading so that you do not accidentally get a card that is partially in the name of another card (rare bug)
#