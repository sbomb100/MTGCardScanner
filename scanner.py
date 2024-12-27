import cv2
import numpy as np
import time

def preprocess_image(img):
    
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

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

   

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    imgContour = img.copy()
    imgConts = img.copy()
   

    card_contour = preprocess_image(img)

    if card_contour is not None:
        cv2.drawContours(img, [card_contour], -1, (0, 255, 0), 2)

    cv2.imshow("Card Detection", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
