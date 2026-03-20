**VisionKey Web - Gesture Control System **
VisionKey Web is an assistive technology project designed using Artificial Intelligence and Computer Vision. It aims to help individuals with physical disabilities (specifically those without hands) to control and interact with computers more easily.
 Features
**Hand Volume Control**: Adjust system volume through specific hand gestures.
**Virtual Mouse**: Control the mouse cursor using eye tracking or hand movements.
**Simple GUI**: A user-friendly interface built using Tkinter for easy navigation.
**Standalone Executable**: The project can run as a portable software (.exe) on Windows without needing Python installed.
Technologies Used
**Python**: The core programming language.
**OpenCV**: Used for camera access and real-time image processing.
**PyAutoGUI**: Handles the automation of mouse movements and volume controls.
**Tkinter**: Used for designing the Graphical User Interface (GUI).
**PyInstaller**: Used to convert the Python script into a standalone executable file.
## 🖥️ Application InterfaceS
![Gesture Control GUI](gui_screenshot.png)
![gui_screenshot](https://github.com/user-attachments/assets/65e253a0-dd9b-4800-86c1-e763ab3effc4)
<video src="https://github.com/user-attachments/assets/08f32c79-2634-48c4-9109-962a29d2decf" width="600" controls></video>
** Usage Instructions**
To interact with the system, follow these simple gestures:
1.🔊 Volume Control
Increase Volume: Bring your Index Finger and Thumb close together and move them upwards.
Decrease Volume: Bring your Index Finger and Thumb close together and move them downwards.
Mute/Unmute: Use a specific "fist" gesture to toggle mute.
2.🖱️ Virtual Mouse
Move Cursor: Move your eyes or head in the direction you want the cursor to go.
Left Click: Blink your left eye or hold your index finger steady for a second.
Right Click: Blink your right eye or use a two-finger gesture.
**How to Run**
**To run this project on your local machine**:
Download or clone this repository.
**Install the required libraries**:
pip install opencv-python pyautogui numpy Pillow
**Run the main application scri**:
ptpython app.py
**📂 Project Structure**
app.py: The main application code and logic.
dist/app.exe: The pre-built executable version of the application.
captured_photo.jpg: A temporary file used for camera testing and verification.
**Developed by: Yedururi Srilakshmi**
