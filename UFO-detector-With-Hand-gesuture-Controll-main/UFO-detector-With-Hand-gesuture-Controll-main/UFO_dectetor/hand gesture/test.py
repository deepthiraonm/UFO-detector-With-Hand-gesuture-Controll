import cv2
import mediapipe as mp
import math
import matplotlib.pyplot as plt

# Serial port configuration
ser = serial.Serial('COM10', 9600)  # Adjust to match your Arduino serial port

# MediaPipe configuration
mp_drawing = mp.solutions.drawing_utils
hand_mpDraw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Function to move servo
def move_servo(angle):
    angle = min(max(angle, 0), 360)  # Ensure angle is within 0-360 degrees
    ser.write(f'{angle}\n'.encode())

# Function to stop servo
def stop_servo():
    ser.write('STOP\n'.encode())

# Function to draw dotted line
def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=20):
    dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
    pts = []
    for i in np.arange(0, dist, gap):
        r = i / dist
        x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
        y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
        p = (x, y)
        pts.append(p)
    if style == 'dotted':
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i % 2 == 1:
                cv2.line(img, s, e, color, thickness)
            i += 1

# Function to check if thumb and middle finger are touching
def are_fingers_touching(lmList):
    thumb_tip = lmList[4]  # Index of thumb tip
    middle_tip = lmList[12]  # Index of middle finger tip
    distance = math.hypot(middle_tip[1] - thumb_tip[1], middle_tip[2] - thumb_tip[2])
    return distance < 50  # Adjust threshold as needed

# Function to map distance to servo angle (0 to 360 degrees)
def map_distance_to_angle(distance):
    min_distance = 50  # Minimum distance for 0 degrees
    max_distance = 300  # Maximum distance for 360 degrees
    # Map distance to angle
    angle = np.interp(distance, [min_distance, max_distance], [0, 360])
    return int(angle)

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        image = cv2.flip(image, 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        exit_x, exit_y, exit_w, exit_h = 700, 100, 400, 100
        cv2.rectangle(image, (exit_x, exit_y), (exit_x + exit_w, exit_y + exit_h), (255, 0, 255), cv2.FILLED)
        cv2.putText(image, "Join your index and middle fingers to exit", (exit_x + 30, exit_y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    if id in [0, 4, 8, 12, 16, 20]:
                        cv2.circle(image, (cx, cy), 15, (255, 255, 255), cv2.FILLED)

                # Draw dotted line between thumb and index finger
                drawline(image, (lmList[4][1], lmList[4][2]), (lmList[8][1], lmList[8][2]), (255, 255, 255), thickness=1, style='dotted', gap=10)

                # Check if thumb and middle finger are touching
                if are_fingers_touching(lmList):
                    # Close the video when middle finger touches thumb
                    cap.release()
                    cv2.destroyAllWindows()
                    break

                # Calculate distance and map it to a full 360-degree angle
                distance = math.hypot(lmList[8][1] - lmList[4][1], lmList[8][2] - lmList[4][2])
                angle = map_distance_to_angle(distance)
                move_servo(angle)  # Move servo motor based on gesture

        else:
            stop_servo()  # Stop servo if no hand is detected

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
