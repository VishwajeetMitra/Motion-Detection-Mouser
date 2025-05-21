# Overview of the project
## Project : Motion detection mouse emulation with voice commandsd.<br/>

A real-time mouse emulation system that emulates the mouse movements and basic mouse functions based on the hand motion.<br/>
It also has support for some of the hard coded voice commands like changing tab, copy, etc.<br/>
The aim of this project is to provide a new way of interacting with the PC without being limited to the basic hardware.<br/>
This program works by plotting 21 points of references to determine the gestures performend and then performs the<br/>
functions associated with a perticular gesture like performing a left click when index and thumb are in contact.<br/>
This program also resolves the issue of the distance from the camera by normalizing the distance required to trigger<br/>
any function with respect to the distance from the camera.<br/>
This program also provides voice command features using google's speech to text library and pyautogui hotkey fuctions.<br/>


### Technologies Used

- **Python**
- **Numpy**
- **Mediapipe**
- **cv2**
- **Speech Recognition**
- **Threading**
- **Pyautogui**
