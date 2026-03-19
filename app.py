import tkinter as tk
import cv2
import pyautogui
from PIL import Image
import warnings
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

# Button 1: Hand Volume Control (Simplified without MediaPipe)
def button1_click():
    print('Hand Volume Control Activated - Simplified Version')
    print("Testing: Press 'u' for manual volume UP, 'd' for manual volume DOWN")
    
    # Try different camera backends
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]
    cap = None
    
    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened with backend: {backend}")
            break
        else:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("Failed to open camera with any backend")
        return

    # Simple color-based hand detection (simplified)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Improved skin color detection ranges
        lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
        lower_skin2 = np.array([160, 20, 70], dtype=np.uint8)
        upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
        
        # Create masks for both ranges
        mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Debug: show mask
        cv2.imshow("Mask", mask)
        
        if contours:
            # Find largest contour (assumed to be hand)
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) > 2000:  # Minimum area threshold
                # Get bounding box
                x, y, w_box, h_box = cv2.boundingRect(largest_contour)
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                
                # Simple gesture detection based on hand position
                hand_center_x = x + w_box // 2
                hand_center_y = y + h_box // 2
                
                # Draw center point
                cv2.circle(frame, (hand_center_x, hand_center_y), 5, (255, 0, 0), -1)
                
                # Map position to volume control
                volume_level = int((hand_center_y / h) * 100)
                volume_level = max(0, min(100, volume_level))
                
                # Draw zone indicators
                cv2.line(frame, (0, int(h * 0.6)), (w, int(h * 0.6)), (0, 255, 0), 2)  # Volume UP line
                cv2.line(frame, (0, int(h * 0.8)), (w, int(h * 0.8)), (255, 0, 0), 2)  # Volume DOWN line
                
                # Add zone labels
                cv2.putText(frame, "VOLUME UP ZONE", (10, int(h * 0.6) - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, "NEUTRAL ZONE", (10, int(h * 0.7)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                cv2.putText(frame, "VOLUME DOWN ZONE", (10, int(h * 0.8) + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
                # Display volume level and position
                cv2.putText(frame, f"Volume: {volume_level}%", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Hand Y: {hand_center_y}/{h}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                # Control volume based on hand height
                if hand_center_y < h * 0.6:  # Hand at top 60% = VOLUME UP
                    cv2.putText(frame, "VOLUME UP", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    print(f"Volume UP triggered! Hand Y: {hand_center_y}, Threshold: {int(h * 0.6)}")
                    pyautogui.press("volumeup")
                    pyautogui.sleep(0.5)
                elif hand_center_y > h * 0.8:  # Hand at bottom 20% = VOLUME DOWN
                    cv2.putText(frame, "VOLUME DOWN", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    print(f"Volume DOWN triggered! Hand Y: {hand_center_y}, Threshold: {int(h * 0.8)}")
                    pyautogui.press("volumedown")
                    pyautogui.sleep(0.5)
                else:
                    cv2.putText(frame, "NEUTRAL", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
                    print(f"Neutral zone. Hand Y: {hand_center_y}, Range: {int(h * 0.6)}-{int(h * 0.8)}")
            else:
                cv2.putText(frame, "No hand detected (too small)", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No hand detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Hand Volume Control", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or 'q' to exit
            print("Exiting Hand Volume Control...")
            break
        elif key == ord('u'):  # Manual volume up test
            print("Manual VOLUME UP test")
            pyautogui.press("volumeup")
        elif key == ord('d'):  # Manual volume down test
            print("Manual VOLUME DOWN test")
            pyautogui.press("volumedown")

    cap.release()
    cv2.destroyAllWindows()

# Button 2: Virtual Mouse (Simplified)
def button2_click():
    print('Virtual Mouse Activated - Simplified Version')
    
    # Try different camera backends
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]
    cap = None
    
    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened with backend: {backend}")
            break
        else:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("Failed to open camera with any backend")
        return
    
    screen_w, screen_h = pyautogui.size()
    prev_x, prev_y = screen_w // 2, screen_h // 2
    click_cooldown = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Simple skin color detection
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (assumed to be hand)
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) > 1000:  # Minimum area threshold
                # Get bounding box
                x, y, w_box, h_box = cv2.boundingRect(largest_contour)
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                
                # Get hand center
                hand_center_x = x + w_box // 2
                hand_center_y = y + h_box // 2
                
                # Map to screen coordinates
                target_x = int((hand_center_x / w) * screen_w)
                target_y = int((hand_center_y / h) * screen_h)
                
                # Apply smoothing
                prev_x = int(prev_x * 0.7 + target_x * 0.3)
                prev_y = int(prev_y * 0.7 + target_y * 0.3)
                
                # Move mouse
                pyautogui.moveTo(prev_x, prev_y)
                
                # Simple click detection (hand size change)
                if w_box * h_box > 15000 and click_cooldown == 0:  # Hand gets bigger = click
                    pyautogui.click()
                    click_cooldown = 30
                    cv2.putText(frame, "CLICK!", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Move Cursor", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Decrease cooldown
        if click_cooldown > 0:
            click_cooldown -= 1

        cv2.imshow("Virtual Mouse", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or 'q' to exit
            print("Exiting Virtual Mouse...")
            break

    cap.release()
    cv2.destroyAllWindows()

# Button 3: Eye Controlled Mouse (Simplified)
def button3_click():
    print('Eye Controlled Mouse Activated - Simplified Version')
    
    # Try different camera backends
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]
    cap = None
    
    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened with backend: {backend}")
            break
        else:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("Failed to open camera with any backend")
        return
    
    screen_w, screen_h = pyautogui.size()
    prev_x, prev_y = screen_w // 2, screen_h // 2

    # Load face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Get first face
            x, y, fw, fh = faces[0]
            face_center_x = x + fw // 2
            face_center_y = y + fh // 2
            
            # Convert to screen coordinates
            target_x = int((face_center_x / w) * screen_w)
            target_y = int((face_center_y / h) * screen_h)
            
            # Apply smoothing
            prev_x = int(prev_x * 0.8 + target_x * 0.2)
            prev_y = int(prev_y * 0.8 + target_y * 0.2)
            
            # Move cursor with boundary check
            if 0 <= prev_x <= screen_w and 0 <= prev_y <= screen_h:
                pyautogui.moveTo(prev_x, prev_y)
            
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
            cv2.circle(frame, (face_center_x, face_center_y), 5, (0, 0, 255), -1)
            
            cv2.putText(frame, "Tracking Face", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Eye Controlled Mouse", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or 'q' to exit
            print("Exiting Eye Controlled Mouse...")
            break

    cap.release()
    cv2.destroyAllWindows()

# Button 4: Capture Photo
def button4_click():
    print('Photo Capture Activated')
    
    # Try different camera backends
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]
    cap = None
    
    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened with backend: {backend}")
            break
        else:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("Failed to open camera with any backend")
        return
    
    count = 0
    photo_path = None

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        cv2.imshow("Photo Capture", frame)
        count += 1
        if count == 50:  # Auto-capture after ~2 seconds
            photo_path = "captured_photo.jpg"
            cv2.imwrite(photo_path, frame)
            print(f"Photo saved as {photo_path}")
            break

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    if photo_path:
        image = Image.open(photo_path)
        image.show()

# GUI Setup
window = tk.Tk()
window.title("Gesture Control GUI (Simplified)")

# Instructions
instructions = tk.Label(window, text="Press ESC or 'q' in any camera window to return to menu", 
                       font=("Arial", 10), fg="blue")
instructions.pack(pady=5)

tk.Button(window, text="Hand Volume Control", command=button1_click, width=20).pack(pady=5)
tk.Button(window, text="Virtual Mouse", command=button2_click, width=20).pack(pady=5)
tk.Button(window, text="Eye Controlled Mouse", command=button3_click, width=20).pack(pady=5)
tk.Button(window, text="Capture Photo", command=button4_click, width=20).pack(pady=5)

def exit_app():
    print("Closing application...")
    window.destroy()
    import sys
    sys.exit(0)

tk.Button(window, text="EXIT", command=exit_app, bg="red", fg="white", width=20).pack(pady=10)

window.mainloop()