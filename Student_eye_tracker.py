import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import threading
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_IRIS = [474, 475, 476, 477]

RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [469, 470, 471, 472]

L_H_LEFT = [33]  # right eye rightmost landmark
L_H_RIGHT = [133]  # right eye leftmost landmark
R_H_LEFT = [362]  # left eye rightmost landmark
R_H_RIGHT = [263]  # left eye leftmost landmark

def euclidean_distance(point1, point2):
    x1, y1 = point1.ravel()
    x2, y2 = point2.ravel()
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def iris_position(iris_center, right_point, left_point):
    center_to_right_dist = euclidean_distance(iris_center, right_point)
    total_distance = euclidean_distance(right_point, left_point)
    ratio = center_to_right_dist / total_distance
    iris_position = ""
    if ratio <= 0.30:
        iris_position = "right"
    elif ratio > 0.42 and ratio <= 0.57:
        iris_position = "center"
    else:
        iris_position = "left"
    return iris_position, ratio

def update_video_stream():
    global img, img_label, cap, eye_tracking_active, led_1, led_2, led_3

    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_h, img_w = frame.shape[:2]

        if eye_tracking_active:
            with mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
            ) as face_mesh:
                results = face_mesh.process(rgb_frame)
                if results.multi_face_landmarks:
                    mesh_points = np.array(
                        [
                            np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                            for p in results.multi_face_landmarks[0].landmark
                        ]
                    )

                    (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
                    (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])
                    center_left = np.array([l_cx, l_cy], dtype=np.int32)
                    center_right = np.array([r_cx, r_cy], dtype=np.int32)
                    cv2.circle(frame, tuple(center_left), int(l_radius), (255, 0, 255), 1, cv2.LINE_AA)
                    cv2.circle(frame, tuple(center_right), int(r_radius), (255, 0, 255), 1, cv2.LINE_AA)
                    cv2.circle(frame, tuple(mesh_points[R_H_RIGHT][0]), 2, (255, 255, 255), -1, cv2.LINE_AA)
                    cv2.circle(frame, tuple(mesh_points[R_H_LEFT][0]), 2, (0, 255, 255), -1, cv2.LINE_AA)
                    cv2.circle(frame, tuple(mesh_points[L_H_RIGHT][0]), 2, (0, 255, 255), -1, cv2.LINE_AA)
                    cv2.circle(frame, tuple(mesh_points[L_H_LEFT][0]), 2, (255, 255, 255), -1, cv2.LINE_AA)

                    iris_pos, ratio = iris_position(
                        center_right, mesh_points[R_H_RIGHT], mesh_points[R_H_LEFT][0])
                    cv2.putText(
                        frame,
                        f"Iris pos: {iris_pos} {ratio:.2f}",
                        (30, 30),
                        cv2.FONT_HERSHEY_PLAIN,
                        1.2,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )

                    # Update LED indicators based on eye tracking results
                    if iris_pos == "right":
                        led_1.configure(bg="red")
                        led_2.configure(bg="gray")
                        led_3.configure(bg="gray")
                    elif iris_pos == "center":
                        led_1.configure(bg="gray")
                        led_2.configure(bg="yellow")
                        led_3.configure(bg="gray")
                    else:
                        led_1.configure(bg="gray")
                        led_2.configure(bg="gray")
                        led_3.configure(bg="green")
                else:
                    # If no face is detected, turn off all LEDs
                    led_1.configure(bg="gray")
                    led_2.configure(bg="gray")
                    led_3.configure(bg="gray")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame back to RGB
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        img_label.configure(image=img)

    # Schedule the next frame update after a delay (10 milliseconds in this case)
    root.after(10, update_video_stream)

def toggle_eye_tracking():
    global eye_tracking_active
    eye_tracking_active = not eye_tracking_active

def on_closing():
    global cap
    cap.release()
    root.destroy()

root = Tk()
root.geometry("800x500")
root.protocol("WM_DELETE_WINDOW", on_closing)

img_label = Label(root)
img_label.pack(side=LEFT, padx=10, pady=10)

# Start button to toggle eye tracking
eye_tracking_active = False
start_button = Button(root, text="Start Test", command=toggle_eye_tracking)
start_button.pack(pady=10)

# LED indicators
led_1 = Label(root, bg="gray", width=10, height=2)
led_1.pack(pady = 5)
led_2 = Label(root, bg="gray", width=10, height=2)
led_2.pack(pady = 5)
led_3 = Label(root, bg="gray", width=10, height=2)
led_3.pack(pady = 5)

cap = cv2.VideoCapture(0)

update_video_stream()  # Start the video streaming and eye tracking loop

root.mainloop()
