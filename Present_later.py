#Importing all the Libraries
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import speech_recognition as sr
import time

# Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,smooth_segmentation=False)

# Set the screen size (you may need to adjust these values for your screen resolution)
screen_width, screen_height = pyautogui.size()

pyautogui.MINIMUM_DURATION= 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0
last_voice_trigger_time = 0
voice_cooldown = 5  # in seconds
global_running_flag = True


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

# Voice command function
def voice_command_listener():
    try: 
        # Define the list of valid commands
        command_list = ["exit","switch tab","copy","paste",]
        # Create a recognizer instance
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            print("Listening for voice commands...")
            
            try:
                # Capture audio input
                audio = recognizer.listen(source, timeout=5,phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                return 
            
            spoken_command = recognizer.recognize_google(audio, language="en-US").lower()
            print(f"Command received: {spoken_command}")
                # Match the spoken command with the command list
            matched_command = next((cmd for cmd in command_list if cmd in spoken_command), None)
                
            if matched_command:
                    print(f"Executing command: {matched_command}")
                    # Execute the corresponding action
                    if matched_command == "exit":
                        pyautogui.hotkey("q")  # Example: Open a new browser tab
                    elif matched_command == "switch tab":
                        pyautogui.hotkey("alt", "tab")
                    elif matched_command == "copy":
                        pyautogui.hotkey("ctrl","c")
                    elif matched_command == "paste":
                        pyautogui.hotkey("ctrl","v")
            else:
                    print("Command not recognized. Please try again.")
    except sr.RequestError as e:
        print(f"Error with the recognition service: {e}")

# Thread management
voice_thread = None
# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened() and global_running_flag :
    ret, frame = cap.read()
    if not ret:
        print("Failed Webcam")
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame with MediaPipe
    results = holistic.process(rgb_frame)

    # Draw hand landmarks
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        
        # Extract hand landmarks
        hand_landmarks = results.left_hand_landmarks.landmark

        if hand_landmarks:

            # ALl the  hand Corrdinates and logic
            middle_finger_tip = hand_landmarks[12]
            index_finger_tip = hand_landmarks[8]
            ring_finger_tip = hand_landmarks[16]
            thumb_tip = hand_landmarks[4]
            x,y = middle_finger_tip.x,middle_finger_tip.y
            nor= normalization(index_finger_tip,middle_finger_tip)
            nor_ring=normalization(thumb_tip,ring_finger_tip)
            nor_ind=normalization(thumb_tip,index_finger_tip)
            thumb_tip = hand_landmarks[4]
            pinky_tip = hand_landmarks[20]
            # Check if the two tips are close to each other
            thumb_pinky_dist = normalization(thumb_tip, pinky_tip)

            # Coordinates for mouse movement
            if nor<1:
                # Map normalized coordinates to screen coordinates
                screen_x, screen_y = map_coordinates(x, y, screen_width, screen_height)
                # Move the mouse cursor
                pyautogui.moveTo(screen_x, screen_y)

            # Conditions for performing a left click
            if nor_ind<1:
                pyautogui.click(button='left')
            # Conditions for performing a right click
            if nor_ring<1:
                pyautogui.click(button='right')
                 
            current_time = time.time()

            # Detect thumb-index-pinky touch gesture for triggering voice commands    
            if thumb_pinky_dist<1 and (voice_thread is None or not voice_thread.is_alive()) and (current_time - last_voice_trigger_time > voice_cooldown):
                # Start voice command listener in a new thread
                last_voice_trigger_time = current_time  
                voice_thread = threading.Thread(target=voice_command_listener)
                voice_thread.start() 

    # Display the resulting frame
    cv2.imshow('Jerry', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        global_running_flag = False
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()