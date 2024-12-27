#used for images
import time
import cv2
#used for matrix and perspective transformations
import numpy as np
#used to read the card texts
import pytesseract

import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #kernel = np.ones((5, 5), np.uint8)
    #imgDil = cv2.dilate(blurred, kernel, iterations=1)
    #sharpened = cv2.filter2D(imgDil, -1, kernel)
    # Detect edges using Canny
    #why 50 vs 150, poerhaps use parameters?
    #threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    #threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")

    #uses gradient detection to try to identify edges on gradscale image
    edges = cv2.Canny(blurred, 50, 150)
   
    #makes list of shapes in the image in a hierarchy  
    #cv2.RETR_EXTERNAL - outermost shapes
    #cv2.CHAIN_APPROX_SIMPLE - remove redundant straight lines
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest rectangular
        largest_contour = max(contours, key=cv2.contourArea)
        approx = cv2.approxPolyDP(largest_contour, 0.02 * cv2.arcLength(largest_contour, True), True)
        
        # Ensure it's a quadrilateral
        if len(approx) == 4:
            return approx  # Return the card contour
    
    
    return None

    #simpler way instead of approxPolyDP - just say "screw it is a rectangle"
    #x, y, w, h = cv2.boundingRect(largest_contour)
    #aspect_ratio = w / h
    #if 0.5 < aspect_ratio < 2:  # Roughly rectangular
    #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

def warp_card(img, contours):
    x, y, w, h = cv2.boundingRect(contours)
    #contours[i][j] where j is the contour and i is the point to be observed
    pts = np.float32([contours[0][0], contours[1][0], contours[2][0], contours[3][0]])
    target = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

    matrix = cv2.getPerspectiveTransform(pts, target)
    return cv2.warpPerspective(img, matrix, (w, h))

def extract_card(img):
    #convert to greyscale for easier reading
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # PSM 6 is for single uniform blocks of text, rather then segmenting text
    card_text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3')  
    return card_text

def getPrice(img):
    card_title = img[25:75, 34:400]
    # cv2.imshow("Card Name",card_title)

    card_name = re.sub('[^a-zA-Z0-9,+ ]', '', pytesseract.image_to_string(card_title))

    print("Card name: ", card_name)

    

#open camera
#cap = cv2.VideoCapture(0)

while True:
    #frame capture
    #success, img = cap.read()
    #if not success:
    #    break
    
    img = cv2.imread("C:\\card.jpg")
    resized_image = cv2.resize(img, None, fx=0.3, fy=0.3)
    #get the large edges
    card_contour = preprocess_image(resized_image)
        

    if card_contour is not None:
        wrapped_card = warp_card(resized_image, card_contour)
       
        cv2.imshow("Warped Card", wrapped_card)
        cv2.drawContours(resized_image, [card_contour], -1, (0, 255, 0), 2)

    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#cap.release()
cv2.destroyAllWindows()
