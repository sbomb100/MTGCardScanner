#used for images
import cv2
#used for matrix and perspective transformations
import numpy as np
#used to read the card texts
import pytesseract
from collections import Counter
import re
import sqlite3

class CardScanner:
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        #weak and strong edge threshholds, gotten from parameter window

        
        imgCanny = cv2.Canny(blurred, self.threshold1, self.threshold2)
    
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
    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # Top-right
        rect[3] = pts[np.argmax(diff)]  # Bottom-left

        return rect

    def warp_card(self, img, contours):
        # Reshape the contour to a 4x2 format
        pts = contours.reshape(4, 2)

        # make sure points are ordered
        ordered_pts = self.order_points(pts)
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
    def extract_card(self, img):
        
        # Ensure the card is in portrait orientation
        height, width = img.shape[:2]
        if width > height:  # Landscape orientation
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        # Dynamically calculate ROI based on card dimensions
        roi_x = int(0.07 * img.shape[1])  # 8% from the left
        roi_y = int(0.05 * img.shape[0])  # 5% from the top
        roi_w = int(0.75 * img.shape[1])  # 85% width TODO EDIT TO FIT LONGER CARDS
        roi_h = int(0.06 * img.shape[0])  # 15% height

        # Crop the ROI from the warped card image
        card_name_roi = img[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
        cv2.imshow("name", card_name_roi)
        # Convert to grayscale for better OCR results
        gray = cv2.cvtColor(card_name_roi, cv2.COLOR_BGR2GRAY)
        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Denoise
        
    
        cv2.imshow("name", binary)
        # Perform OCR on the cropped ROI
 
        card_name = [
            re.sub('[^a-zA-Z,+\', ]', '', pytesseract.image_to_string(binary)).strip() 
            for _ in range(5)]
        name_counts = Counter(card_name)
        most_common_name, count = name_counts.most_common(1)[0]
        if count > 2:  # Ensure at least 2 out of 3 scans agree
            return most_common_name
        else:
            return ""



    #check the scryfall databse for the card via name
    def update_database(self, card_data):
        self.all_cursor.execute("""SELECT id, name, set_name, type, rarity, mana_cost, oracle_text
                        FROM cards WHERE name = ?""", (card_data,))
        card = self.all_cursor.fetchone()
        if card:
            self.last_card = card_data.strip()
            print(f"Found card: {card}")
            #fetch the price
            self.all_cursor.execute("""
            SELECT card_id, usd, usd_foil
            FROM prices
            WHERE card_id = (SELECT id FROM cards WHERE name = ?)
            """, (card_data,))

            price = self.all_cursor.fetchone()

            if price:
                print(f"Prices for '{card_data}': {price}")
                
                self.my_cursor.execute("SELECT count FROM cards WHERE id = ?", (card[0],))
                existing_card = self.my_cursor.fetchone()
                #fetch the price
                if (existing_card):
                    new_count = existing_card[0] + 1  # Add the new count to the existing one
                    print(f"more cards, now at: {new_count} of {card_data}!")
                    self.my_cursor.execute("""
                    UPDATE cards
                    SET count = ?
                    WHERE id = ?
                    """, (new_count, card[0]))
                    self.my_cards.commit()
                    return 0
                else:
                    # If the card does not exist, insert a new card with count
                    print("new card!\n")
                    self.my_cursor.execute("""
                    INSERT INTO cards (id, name, set_name, type, rarity, mana_cost, oracle_text, count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        *card[:7],
                        1
                    ))

                    self.my_cursor.execute("""
                    INSERT INTO prices (card_id, usd, usd_foil)
                    VALUES (?, ?, ?)
                    """, (
                        price[:3]
                    ))
                    print(f"Card Added -- {card[1]}")
                    self.my_cards.commit()
                    return 1
            else:
                print(f"Price not found")
                return -1
        else:
            return -1

        
    def __init__(self, camera_index=1):
        self.threshold1 = 50
        self.threshold2 = 150
        self.cap = cv2.VideoCapture(camera_index)
        self.all_cards = sqlite3.connect("databases/cards.db")
        self.my_cards = sqlite3.connect("databases/MTGPersonalCollection.db")
        self.last_card = ""
        self.all_cursor = self.all_cards.cursor()
        self.my_cursor = self.my_cards.cursor()

        

    #open camera
    def read_frame(self):
            #frame capture
            success, img = self.cap.read()

            if not success:
                print("ERROR: Camera Broke")
                return None
            else:
                return img

    def analyze_card(self, img):
        #get the large edges
            card_contour = self.preprocess_image(img)
                
            if card_contour is not None:
                wrapped_card = self.warp_card(img, card_contour)
                card_data = self.extract_card(wrapped_card)
                
            
                cv2.imshow("Warped", wrapped_card)
                #print(f"{card_data} is {last_card} \n")
                if card_data.strip() == "":
                    #print("DEBUG: Card data is empty, skipping frame.")
                    return ""

                if card_data.strip() == self.last_card:
                    #print("DEBUG: Duplicate card detected, skipping database update.")
                    return ""
                else: 
                    #now that we have the name, check databse
                    ret = self.update_database(card_data)
                    if ret > -1:
                        return card_data.strip()
                    else:
                        return ""
            else:
                return ""
                    
            
    def shutdown(self):
        self.cap.release()
        self.all_cards.close()
        self.my_cards.close()
        cv2.destroyAllWindows()


#TODO:
#make so any orientation will get flipped upright.
#double check the card reading so that you do not accidentally get a card that is partially in the name of another card (rare bug)
# may want to edit so that the name section will narrow or broaden based on abilityto capture mana or not full name
# flip card if cant read anything