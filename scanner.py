#used for images
import time
import cv2
#used for matrix and perspective transformations
import numpy as np
#used to read the card texts
import pytesseract

import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Create a window
cv2.namedWindow("Trackbars")

def nothing(x):
    pass
# Create two trackbars to control the Canny edge detection thresholds
cv2.createTrackbar("Threshold1", "Trackbars", 50, 255, nothing)
cv2.createTrackbar("Threshold2", "Trackbars", 150, 255, nothing)


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

def extract_card(img):
    #convert to greyscale for easier reading
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # PSM 6 is for single uniform blocks of text, rather then segmenting text
    card_text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3')  
    lines = card_text.splitlines()

    return re.sub('[^a-zA-Z0-9,+ ]', '', lines[0])

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
    time.sleep(1)

    img = cv2.imread("C:\card2.jpg")
    resized_image = cv2.resize(img, None, fx=0.3, fy=0.3)
    #get the large edges
    card_contour = preprocess_image(resized_image)
        

    if card_contour is not None:
        wrapped_card = warp_card(resized_image, card_contour)
        card_data = extract_card(wrapped_card)
        print(card_data)
        #cv2.imshow("Original", resized_image)
        #cv2.imshow("Contours", cv2.drawContours(resized_image.copy(), [card_contour], -1, (0, 255, 0), 2))
        cv2.imshow("Warped", wrapped_card)
        

    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#cap.release()
cv2.destroyAllWindows()


#NEXT STEPS 
#- fix reading of title: limit where tesseract reads
#- cache image into database obj
#- 