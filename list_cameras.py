import cv2

def list_cameras():
    available_cameras = []
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            available_cameras.append(i)
            cap.release()  # Release the camera resource
    if not available_cameras:
        print("No cameras found.")
    return available_cameras

# List all cameras
cameras = list_cameras()
print("Available camera indices:", cameras)
