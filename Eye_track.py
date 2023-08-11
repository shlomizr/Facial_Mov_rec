#! /usr/bin/python3

import cv2 as cv
import numpy as np
import mediapipe as mp
import math
import time
import tkinter as tk
from PIL import Image, ImageTk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import RPi.GPIO as GPIO
from time import sleep
import re
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
    elif ratio > 0.40 and ratio <= 0.50:
        iris_pos = "center"
    else:
        iris_pos = "left"
    return iris_pos, ratio

def emailToInspector(SdudentId, imagePath):
    smtpUser = 'finalprog2023@gmail.com'
    smtpPass = 'edheeqzmjfpulvpm'

    toADD = 'finalprog2023@gmail.com'
    fromADD = smtpUser

    t =time.localtime()
    t_date = time.strftime('%D',t)
    t_time = time.strftime('%H:%M:%S',t)

    subject = "Student number: " + SdudentId + " was suspected of copying"

    msg = MIMEMultipart()
    msg['From'] = fromADD
    msg['To'] = toADD
    msg['Subject'] = subject

    body = "Student number: " + SdudentId + "  was suspected of copying while doiung exam at: " + t_date + " " + t_time 
    msg.attach(MIMEText(body, 'plain'))

    with open("Photo1.jpg", "rb") as image_file:
        image = MIMEImage(image_file.read(), name=imagePath)
        msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(smtpUser, smtpPass)
    s.sendmail(fromADD, toADD, msg.as_string())
    s.quit()

def VoiceMess():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pe = 17
    GPIO.setup(pe, GPIO.OUT)
    GPIO.output(pe,0)
    GPIO.output(pe, 1)
    time.sleep(0.1)
    GPIO.output(pe, 0)

def studentInfo():
    f = open('studentInfo.txt', 'r')
    line = f.readlines()
    info = line[0]
    info = re.search(r'(^\w+),(\s+\w+),(\s+\S+)',info)
    studentName = info.group(1)
    studentId = info.group(2)
    studentEmail = info.group(3)
    f.close
    return studentName,studentId,studentEmail

def start_monitoring(root, studentId,led1,led2,led3):
    cap = cv.VideoCapture(0)

    ledCnt = 1
    cntRight = 0
    cntLeft = 0
    cntCenter = 0
    done = 0

    with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks = True,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
    ) as face_mesh:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.flip(frame, 1)
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img_h, img_w = frame.shape[:2]
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
               mesh_points = np.array(
                    [
                        np.multiply([p.x,p.y], [img_w,img_h]).astype(int)
                        for p in results.multi_face_landmarks[0].landmark
                    ]
                )
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
               print(iris_pos)
                # Update LED colors based on iris position
               if iris_pos == "center":
                   cntCenter = cntCenter +1
                   if cntCenter == 90:
                       cntLeft = 0
                       cntRight = 0
                       cntCenter = 0

               if iris_pos == "left":
                   cntLeft = cntLeft + 1
                   if cntLeft > 70: 
                       VoiceMess()
                       if led1.cget('bg') == "#31EC47":
                           led1.config(bg='red')
                           cntLeft = 0
                           cv.imwrite("Photo1.jpg", frame)
                           emailToInspector(studentId,"Photo1.jpg")
                       elif led2.cget('bg') == "#31EC47":
                           led2.config(bg='red')
                           cntLeft = 0
                           cv.imwrite("Photo2.jpg", frame)
                           emailToInspector(studentId,"Photo2.jpg")
                       else:
                           led3.config(bg='red')
                           cv.imwrite("Photo3.jpg", frame)
                           emailToInspector(studentId,"Photo3.jpg")
                           done = 1
                           break


               if iris_pos == "right":
                   cntRight = cntRight + 1
                   if cntRight > 70:
                       VoiceMess()
                       if led1.cget('bg') == "#31EC47":
                           led1.config(bg='red')
                           cntRight = 0
                           cv.imwrite("Photo1.jpg", frame)
                           emailToInspector(studentId,"Photo1.jpg")
                       elif led2.cget('bg')== "#31EC47":
                           led2.config(bg='red')
                           cntRight = 0
                           cv.imwrite("Photo2.jpg", frame)
                           emailToInspector(studentId,"Photo2.jpg")
                       else:
                           led3.config(bg='red')
                           cv.imwrite("Photo3.jpg", frame)
                           emailToInspector(studentId,"Photo3.jpg")
                           done = 1
                           break
 

            cv.imshow('Student Video',frame)

            key = cv.waitKey(1)
            if key == ord('q'):
                break
            if done == 1:
                break

            root.update()
            
    cap.release()
    cv.destroyAllWindows()

def open_gui(studentName,studentId):
    root = tk.Tk()
    root.title("Student Monitoring")
    #root.geometry("430x100")
    root.configure(bg='#EDEDED')

    # Create LED indicators
    led1_color = "#31EC47"
    led2_color = "#31EC47"
    led3_color = "#31EC47"
        

    # Create Labels for LED indicators
    led1 = tk.Label(root, text="WARNING 1", bg=led1_color, padx=20, pady=20)
    led2 = tk.Label(root, text="WARNING 2", bg=led2_color, padx=20, pady=20)
    led3 = tk.Label(root, text="WARNING 3", bg=led3_color, padx=20, pady=20)
    
    
    # Create Labels for student information
    student_id_label = tk.Label(root, text=f"Student ID: {studentId}", bg='#F2F2F2', fg='#333333')
    student_name_label = tk.Label(root, text=f"Student Name: {studentName}", bg='#F2F2F2', fg='#333333')

    # Create Start Button
    start_button = tk.Button(root, text="Start Monitoring", command=lambda: start_monitoring(root, studentId,led1,led2,led3),padx=20, pady=10, bg="#4285F4", fg="white")
    exit_button = tk.Button(root, text="Exit", command=root.quit, padx=20, pady=10, bg="#FF5733", fg="white")


    # Create layout
    led1.grid(row=2, column=0, padx=10, pady=10)
    led2.grid(row=2, column=1, padx=10, pady=10)
    led3.grid(row=2, column=2, padx=10, pady=10)
    student_id_label.grid(row=0, columnspan=3, pady=(20, 5))
    student_name_label.grid(row=1, columnspan=3, pady=(0, 5))
    start_button.grid(row=3, columnspan=3, pady=20)
    exit_button.grid(row=4, column=1, pady=20, padx=(5, 10))

    root.mainloop()

if __name__ == "__main__":
    studentName,studentId, studentEmail = studentInfo()
    open_gui(studentName,studentId)
