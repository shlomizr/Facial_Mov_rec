#! /usr/bin/python3

import cv2 as cv
import numpy as np
import mediapipe as mp
import math
import os
import tkinter as tk
from PIL import Image, ImageTk
import smtplib
import RPi.GPIO as GPIO
from time import sleep
mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
RIGHT_IRIS = [474, 475, 476, 477]

RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [469, 470, 471, 472]

L_H_LEFT = [33] # right eye right most landmark
L_H_RIGHT = [133] # right eye left most landmark
R_H_LEFT = [362] # left eye right most landmark
R_H_RIGHT = [263] # left eye left most landmark


def euclidean_distance(point1, point2):
    x1,y1 = point1.ravel()
    x2,y2 = point2.ravel()
    distance = math.sqrt((x2-x1)**2+(y2-y1)**2)
    return distance

def iris_position(iris_center, right_point, left_point):
    center_to_right_dist = euclidean_distance(iris_center, right_point)
    total_distance = euclidean_distance(right_point, left_point)
    ratio = center_to_right_dist/total_distance
    iris_pos = ""
    if ratio <= 0.30:
        iris_pos = "right"
    elif ratio > 0.42 and ratio <= 0.60:
        iris_pos = "center"
    else:
        iris_pos = "left"
    return iris_pos, ratio

def emailToInspector(SdudentId):
    smtpUser = 'finalprog2023@gmail.com'
    smtpPass = 'edheeqzmjfpulvpm'

    toADD = 'finalprog2023@gmail.com'
    fromADD = smtpUser

    subject = "Student: " + SdudentId + " varification"
    header = 'To:' + toADD + "\n" + "From:" + fromADD +"\n" "Subject:" + subject
    body = "Student number: " + SdudentId + " had been varifed and will start the exam soon." 
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtpUser,smtpPass)
    s.sendmail(fromADD, toADD, header + "\n\n"+ body)

    s.quit()


def VoiceMess():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pe = 7
    GPIO.setup(pe, GPIO.OUT)
    GPIO.output(pe,0)
    sleep(1)
    GPIO.output(pe, 1)
    sleep(5)
    GPIO.output(pe, 0)
    sleep(1)

cap = cv.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks = True,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
    ) as face_mesh:
        # Create tkinter window
        root = tk.Tk()
        root.title("Student Monitoring")

        # Create LED indicators
        led1_color = "green"
        led2_color = "green"
        led3_color = "green"

        led1 = tk.Label(root, text="WARNING 1", bg=led1_color, padx=20, pady=20)
        led2 = tk.Label(root, text="WARNING 2", bg=led2_color, padx=20, pady=20)
        led3 = tk.Label(root, text="WARNING 3", bg=led3_color, padx=20, pady=20)
        ledCnt = 1


        # Create layout
        led1.grid(row=0, column=0, padx=10, pady=10)
        led2.grid(row=0, column=1, padx=10, pady=10)
        led3.grid(row=0, column=2, padx=10, pady=10)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.flip(frame, 1)
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img_h, img_w = frame.shape[:2]
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
               # print(results.multi_face_landmarks[0].landmark)
               mesh_points = np.array(
                    [
                        np.multiply([p.x,p.y], [img_w,img_h]).astype(int)
                        for p in results.multi_face_landmarks[0].landmark
                    ]
                )
               # print(mesh_points.shape)
               # cv.polylines(frame, [mesh_points[LEFT_IRIS]], True, (0,255,0), 1, cv.LINE_AA)
               # cv.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (0,255,0), 1, cv.LINE_AA)
               (l_cx, l_cy), l_raduis = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
               (r_cx, r_cy), r_raduis = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
               center_left = np.array([l_cx, l_cy], dtype=np.int32)
               center_right = np.array([r_cx, r_cy], dtype=np.int32)
               cv.circle(frame, tuple(center_left), int(l_raduis),  (255,0,255), 1, cv.LINE_AA)
               cv.circle(frame, tuple(center_right), int(r_raduis),  (255,0,255), 1, cv.LINE_AA)
               cv.circle(frame, tuple(mesh_points[R_H_RIGHT][0]), 2, (255,255,255), -1, cv.LINE_AA)
               cv.circle(frame, tuple(mesh_points[R_H_LEFT][0]), 2, (0,255,255), -1, cv.LINE_AA)
               cv.circle(frame, tuple(mesh_points[L_H_RIGHT][0]), 2, (0,255,255), -1, cv.LINE_AA)
               cv.circle(frame, tuple(mesh_points[L_H_LEFT][0]), 2, (255,255,255), -1, cv.LINE_AA)
               
               iris_pos, ratio = iris_position(
                   center_right, mesh_points[R_H_RIGHT], mesh_points[R_H_LEFT][0])
               cv.putText(
                   frame,
                   f"Iris pos: {iris_pos} {ratio:.2f}",
                   (30, 30),
                   cv.FONT_HERSHEY_PLAIN,
                   1.2,
                   (0,255,0),
                   1,
                   cv.LINE_AA,
               )

            # Update GUI
            root.update()

            cv.imshow('Student Video',frame)

            key = cv.waitKey(1)
            if key == ord('q'):
                break
            
cap.release()
cv.destroyAllWindows()
root.destroy()