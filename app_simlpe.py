import tkinter as tk
import cv2
import mediapipe as mp
import pyautogui
from PIL import Image
import warnings

# Suppress MediaPipe warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

# Initialize MediaPipe solutions
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Button 1: Hand Volume Control
def button1_click():
    print('Hand Volume Control Activated')
    
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
    
    hands = mp_hands.Hands(
        max_num_hands=1, 
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    draw = mp_drawing

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                thumb = hand_landmarks.landmark[4]
                index = hand_landmarks.landmark[8]

                x1, y1 = int(index.x * w), int(index.y * h)
                x2, y2 = int(thumb.x * w), int(thumb.y * h)

                cv2.circle(frame, (x1, y1), 8, (0, 255, 255), -1)
                cv2.circle(frame, (x2, y2), 8, (0, 0, 255), -1)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                distance = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
                
                # Map distance to volume range (0-100)
                max_distance = 300  # Maximum expected distance
                volume_level = min(100, max(0, (distance / max_distance) * 100))
                
                cv2.putText(frame, f"Volume: {int(volume_level)}%", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Distance: {int(distance)}px", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Control volume based on distance with proper thresholds
                if distance > 200:
                    cv2.putText(frame, "VOLUME UP", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    pyautogui.press("volumeup")
                    pyautogui.sleep(0.3)  # Longer delay to prevent rapid presses
                elif distance < 80:
                    cv2.putText(frame, "VOLUME DOWN", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    pyautogui.press("volumedown")
                    pyautogui.sleep(0.3)  # Longer delay to prevent rapid presses
                else:
                    cv2.putText(frame, "NEUTRAL ZONE", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        cv2.imshow("Hand Volume Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# Button 2: Virtual Mouse
def button2_click():
    print('Virtual Mouse Activated')
    
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
    
    hands = mp_hands.Hands(
        max_num_hands=1, 
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    draw = mp_drawing
    screen_w, screen_h = pyautogui.size()
    
    # Variables for smooth control
    prev_x, prev_y = 0, 0
    click_cooldown = 0
    click_threshold = 30  # Distance threshold for click
    smoothing = 0.7  # Smoothing factor for movement

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get key landmarks
                index = hand_landmarks.landmark[8]
                thumb = hand_landmarks.landmark[4]
                middle = hand_landmarks.landmark[12]
                wrist = hand_landmarks.landmark[0]

                # Convert to screen coordinates
                ix, iy = int(index.x * w), int(index.y * h)
                tx, ty = int(thumb.x * w), int(thumb.y * h)
                mx, my = int(middle.x * w), int(middle.y * h)
                wx, wy = int(wrist.x * w), int(wrist.y * h)

                # Calculate screen position with proper mirroring
                target_x = (screen_w / w) * ix  # Remove mirroring for natural movement
                target_y = (screen_h / h) * iy
                
                # Apply smoothing for natural movement
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = target_x, target_y
                else:
                    prev_x = prev_x * smoothing + target_x * (1 - smoothing)
                    prev_y = prev_y * smoothing + target_y * (1 - smoothing)
                
                # Only move if position changed significantly
                if abs(prev_x - target_x) > 2 or abs(prev_y - target_y) > 2:
                    pyautogui.moveTo(prev_x, prev_y)

                # Calculate distance between thumb and index for click
                distance = ((ix - tx)**2 + (iy - ty)**2) ** 0.5
                
                # Visual feedback
                cv2.circle(frame, (ix, iy), 8, (0, 255, 0), -1)
                cv2.circle(frame, (tx, ty), 8, (255, 0, 0), -1)
                cv2.line(frame, (ix, iy), (tx, ty), (0, 255, 255), 2)
                
                # Display distance and status
                cv2.putText(frame, f"Distance: {int(distance)}px", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Click detection with cooldown
                if distance < click_threshold and click_cooldown == 0:
                    pyautogui.click()
                    click_cooldown = 30  # Prevent multiple rapid clicks
                    cv2.putText(frame, "CLICK!", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                elif distance < click_threshold:
                    cv2.putText(frame, "Ready to Click", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                else:
                    cv2.putText(frame, "Move Cursor", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        # Decrease cooldown
        if click_cooldown > 0:
            click_cooldown -= 1

        cv2.imshow("Virtual Mouse", frame)
        ifimport pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report

iris = load_iris()

df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['target'] = iris.target
df['flower_name'] = df.target.apply(lambda x: iris.target_names[x])

print(df.head())

df0 = df[df.target == 0]
df1 = df[df.target == 1]
df2 = df[df.target == 2]

plt.figure(figsize=(6,5))
plt.xlabel('Sepal Length (cm)')
plt.ylabel('Sepal Width (cm)')

plt.scatter(df0['sepal length (cm)'], df0['sepal width (cm)'],
            color="green", marker='+', label="Setosa")
plt.scatter(df1['sepal length (cm)'], df1['sepal width (cm)'],
            color="blue", marker='.', label="Versicolor")
plt.scatter(df2['sepal length (cm)'], df2['sepal width (cm)'],
            color="red", marker='*', label="Virginica")

plt.legend()
plt.show()

plt.figure(figsize=(6,5))
plt.xlabel('Petal Length (cm)')
plt.ylabel('Petal Width (cm)')

plt.scatter(df0['petal length (cm)'], df0['petal width (cm)'],
            color="green", marker='+', label="Setosa")
plt.scatter(df1['petal length (cm)'], df1['petal width (cm)'],
            color="blue", marker='.', label="Versicolor")
plt.scatter(df2['petal length (cm)'], df2['petal width (cm)'],
            color="red", marker='*', label="Virginica")

plt.legend()
plt.show()

X = df.drop(['target','flower_name'], axis='columns')
y = df.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=1
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

accuracy = knn.score(X_test, y_test)
print("\nModel Accuracy:", accuracy)

sample = pd.DataFrame([[4.8, 3.0, 1.5, 0.3]], columns=X.columns)
prediction = knn.predict(sample)
print("Predicted class:", iris.target_names[prediction][0])

y_pred = knn.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(7,5))
sns.heatmap(cm, annot=True, cmap="Blues", fmt='d',
            xticklabels=iris.target_names,
            yticklabels=iris.target_names)

plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred,target_names=iris.target_names)) cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# Button 3: Eye Controlled Mouse
def button3_click():
    print('Eye Controlled Mouse Activated')
    
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
    
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    screen_w, screen_h = pyautogui.size()
    
    # Variables for smooth control
    prev_x, prev_y = screen_w // 2, screen_h // 2
    blink_cooldown = 0
    blink_threshold = 0.015  # Threshold for blink detection
    smoothing = 0.3  # Lower smoothing for responsive eye tracking
    
    # Eye landmarks for better tracking
    LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 373, 380, 381, 382, 383, 374, 390]
    LEFT_IRIS = [474, 475, 476, 477]
    RIGHT_IRIS = [469, 470, 471, 472]

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            landmarks = result.multi_face_landmarks[0].landmark
            
            # Calculate eye centers for more stable tracking
            left_eye_center = [0, 0]
            right_eye_center = [0, 0]
            
            # Get left eye landmarks
            for idx in LEFT_EYE:
                left_eye_center[0] += landmarks[idx].x
                left_eye_center[1] += landmarks[idx].y
            left_eye_center[0] /= len(LEFT_EYE)
            left_eye_center[1] /= len(LEFT_EYE)
            
            # Get right eye landmarks
            for idx in RIGHT_EYE:
                right_eye_center[0] += landmarks[idx].x
                right_eye_center[1] += landmarks[idx].y
            right_eye_center[0] /= len(RIGHT_EYE)
            right_eye_center[1] /= len(RIGHT_EYE)
            
            # Use iris center for more precise tracking
            left_iris = landmarks[473]  # Left iris center
            right_iris = landmarks[468]  # Right iris center
            
            # Average eye position for cursor control
            eye_x = (left_iris.x + right_iris.x) / 2
            eye_y = (left_iris.y + right_iris.y) / 2
            
            # Convert to screen coordinates
            target_x = (screen_w * eye_x)  # Remove mirroring
            target_y = (screen_h * eye_y)
            
            # Apply smoothing
            prev_x = prev_x * smoothing + target_x * (1 - smoothing)
            prev_y = prev_y * smoothing + target_y * (1 - smoothing)
            
            # Move cursor with boundary check
            if 0 <= prev_x <= screen_w and 0 <= prev_y <= screen_h:
                pyautogui.moveTo(prev_x, prev_y)
            
            # Blink detection using eye aspect ratio
            left_eye_top = landmarks[159].y
            left_eye_bottom = landmarks[145].y
            right_eye_top = landmarks[386].y
            right_eye_bottom = landmarks[374].y
            
            left_eye_height = abs(left_eye_top - left_eye_bottom)
            right_eye_height = abs(right_eye_top - right_eye_bottom)
            avg_eye_height = (left_eye_height + right_eye_height) / 2
            
            # Visual feedback
            # Draw eye landmarks
            for idx in LEFT_EYE + RIGHT_EYE:
                x, y = int(landmarks[idx].x * w), int(landmarks[idx].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            # Draw iris centers
            left_iris_x, left_iris_y = int(left_iris.x * w), int(left_iris.y * h)
            right_iris_x, right_iris_y = int(right_iris.x * w), int(right_iris.y * h)
            cv2.circle(frame, (left_iris_x, left_iris_y), 5, (255, 0, 0), -1)
            cv2.circle(frame, (right_iris_x, right_iris_y), 5, (255, 0, 0), -1)
            
            # Draw tracking point
            track_x, track_y = int(eye_x * w), int(eye_y * h)
            cv2.circle(frame, (track_x, track_y), 8, (0, 0, 255), -1)
            
            # Display info
            cv2.putText(frame, f"Eye Height: {avg_eye_height:.3f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Blink detection with cooldown
            if avg_eye_height < blink_threshold and blink_cooldown == 0:
                pyautogui.click()
                blink_cooldown = 30  # Prevent multiple rapid clicks
                cv2.putText(frame, "BLINK CLICK!", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            elif avg_eye_height < blink_threshold:
                cv2.putText(frame, "Ready to Click", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            else:
                cv2.putText(frame, "Tracking Eyes", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        # Decrease cooldown
        if blink_cooldown > 0:
            blink_cooldown -= 1

        cv2.imshow("Eye Controlled Mouse", frame)
        if cv2.waitKey(1) & 0xFF == 27:
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
        if count == 50:
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
window.title("Gesture Control GUI")

tk.Button(window, text="Hand Volume Control", command=button1_click).pack(pady=5)
tk.Button(window, text="Virtual Mouse", command=button2_click).pack(pady=5)
tk.Button(window, text="Eye Controlled Mouse", command=button3_click).pack(pady=5)
tk.Button(window, text="Capture Photo", command=button4_click).pack(pady=5)
tk.Button(window, text="EXIT", command=window.quit, bg="red", fg="white").pack(pady=10)

window.mainloop()