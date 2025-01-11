import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,smooth_segmentation=False)

# Set the screen size (you may need to adjust these values for your screen resolution)
screen_width, screen_height = pyautogui.size()

# Function to map normalized coordinates to screen coordinates
def map_coordinates(x, y, width, height):
    screen_x = int(x * width)
    screen_y = int(y * height)
    return screen_x, screen_y

def normalization(a,b):
    dist_x=a.x-b.x
    dist_y=a.y-b.y
    a_z=a.z
    b_z=b.z
    depth=abs(a.z+b.z)/2
    nor=np.sqrt(dist_x**2+dist_y**2)/(depth) if depth!=0 else float('inf')
    return nor

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame with MediaPipe
    results = holistic.process(rgb_frame)
    pyautogui.MINIMUM_DURATION= 0
    pyautogui.MINIMUM_SLEEP = 0
    pyautogui.PAUSE = 0
    
    # Draw hand landmarks
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        
        # Extract hand landmarks
        hand_landmarks = results.left_hand_landmarks.landmark
        if hand_landmarks:
            # Use the tip of the index finger (landmark 8)
            middle_finger_tip = hand_landmarks[12]
            index_finger_tip = hand_landmarks[8]
            index_finger_2nd = hand_landmarks[16]
            thumb_tip = hand_landmarks[4]
            pinky_tip = hand_landmarks[20]
            x,y = middle_finger_tip.x,middle_finger_tip.y
            nor= normalization(index_finger_tip,middle_finger_tip)
            nor_ring=normalization(thumb_tip,index_finger_2nd)
            nor_ind=normalization(thumb_tip,index_finger_tip)
            nor_pinky=normalization(thumb_tip,pinky_tip)
            # Coordinates for mouse movement
            if nor<1:
                # Map normalized coordinates to screen coordinates
                screen_x, screen_y = map_coordinates(x, y, screen_width, screen_height)
                # Move the mouse cursor
                pyautogui.moveTo(screen_x, screen_y)
            # Conditions for performing a click
            if nor_ind<1:
                pyautogui.click(button='left')
                
            if nor_ring<1:
                pyautogui.click(button='right')
            if nor_pinky<1:
                pyautogui.dragTo(screen_x,screen_y,button='left')
            

    # Display the resulting frame
    cv2.imshow('Jerry', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()