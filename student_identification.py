#! /usr/bin/python3

import tkinter as tk
import cv2
import imutils
import pickle
import time
import face_recognition
from imutils.video import VideoStream
from imutils.video import FPS
import smtplib
import RPi.GPIO as GPIO
from time import sleep



def emailToStudent(studentID,studentEmail):
    smtpUser = 'finalprog2023@gmail.com'
    smtpPass = 'edheeqzmjfpulvpm'

    toADD = studentEmail
    fromADD = smtpUser
    t =time.localtime()
    t_date = time.strftime('%D',t)
    t_time = time.strftime('%H:%M:%S',t)

    subject = "Verification exam email"
    header = 'To:' + toADD + "\n" + "From:" + fromADD +"\n" "Subject:" + subject
    body = "Hello," + "\n" + "Your ID (" + studentID + ")" "had been verifed at: " + t_date + " " + t_time + ".\n" + "Good luck" 

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtpUser,smtpPass)
    s.sendmail(fromADD, toADD, header + "\n\n"+ body)

    s.quit()

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
    pe = 4
    GPIO.setup(pe, GPIO.OUT)
    GPIO.output(pe,0)
    GPIO.output(pe, 1)
    sleep(0.1)
    GPIO.output(pe, 0)

def createDict():
    student_db = {
        "123456789": {
            "name" : "Shlomi",
            "email" : "shlomizr71@gmail.com"
            },
        "111111111": {
            "name" : "Barbi" , 
            "email" : "Barbi@gmail.com"
            },
        "456789123": {
            "name" : "Ken",
            "email" : "Ken@gmail.com"
            }
    }
    return student_db

def checkID(user_id_entry, student_dict):
    user_id = user_id_entry.get()
    if user_id in student_dict:
        openFaceRec(user_id, student_dict)
    else:
        print("Invalid User ID. Please re-enter.")

    # Clear the user ID entry field
    user_id_entry.delete(0, tk.END)

def saveInfo(name, id, email):
    f = open("studentInfo.txt","w")
    f.write(name + ", " + id + ", " + email)
    f.close



def openGui(student_dict):
    window = tk.Tk()
    window.title("Face Recognition")

    # Set the font size
    font_size = 12
    # Calculate the center position of the screen
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 300
    window_height = 150
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create User ID label and entry
    user_id_label = tk.Label(window, text="User ID (9 digits):", font=("Arial", font_size))
    user_id_label.pack()

    user_id_entry = tk.Entry(window, font=("Arial", font_size))
    user_id_entry.pack()

    # Create Open button
    open_button = tk.Button(window, text="Open", command=lambda: checkID(user_id_entry, student_dict),
                            font=("Arial", font_size))
    open_button.pack()

    # Bind Enter key press event to the Open button
    window.bind("<Return>", lambda event: open_button.invoke())

    # Create Exit button
    exit_button = tk.Button(window, text="Exit", command=window.quit, font=("Arial", font_size))
    exit_button.pack()

    # Create result label to display messages
    result_label = tk.Label(window, text="", font=("Arial", font_size))
    result_label.pack()

    # Start the GUI event loop
    window.mainloop()

def openFaceRec(user_id, student_dict):
    print("[INFO] Starting facial recognition...")
    print("User ID:", user_id)

    encodings_file = "encodings.pickle"

    student_info = student_dict[user_id]
    student_email = student_info["email"]
    student_name = student_info["name"]
  

    # Load the known faces and encodings
    print("[INFO] Loading encodings...")
    data = pickle.loads(open(encodings_file, "rb").read())

    # Initialize video stream and allow the camera to warm up
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    # Initialize the FPS counter
    fps = FPS().start()

    match_found = False

    while not match_found:
        cnt = 0

        # Main loop for video stream processing
        while True:
            # Read a frame from the video stream and resize it
            frame = vs.read()
            frame = imutils.resize(frame, width=500)

            # Detect face locations in the frame
            boxes = face_recognition.face_locations(frame)

            # Compute facial encodings for each face
            encodings = face_recognition.face_encodings(frame, boxes)

            # Initialize a list of names for recognized faces
            names = []

            # Loop over the facial encodings
            for encoding in encodings:
                # Attempt to match each face in the frame with known encodings
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                # Check if there is a match
                if True in matches:
                    # Find the indexes of all matched faces
                    matched_idxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # Loop over the matched indexes and count the votes for each recognized face
                    for i in matched_idxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    if name == student_name:
                        cnt += 1
                        if cnt == 5:
                            print("Match found!")
                            emailToStudent(user_id,student_email)
                            emailToInspector(user_id)
                            VoiceMess()
                            saveInfo(student_name,user_id,student_email)
                            match_found = True
                            break
                    else:
                        cnt = 0

                # Add the recognized name to the list
                names.append(name)

            # Loop over the recognized faces and draw bounding boxes and names
            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the frame
            cv2.imshow("Facial Recognition", frame)

            # Check for 'q' key press to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Update the FPS counter
            fps.update()

            if match_found:
                break

        if not match_found:
            print("No match found. Please re-enter your ID.")
            break

    # Stop the FPS counter and display information
    fps.stop()
    print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] Approximate FPS: {:.2f}".format(fps.fps()))

    # Cleanup
    cv2.destroyAllWindows()
    vs.stop()


if __name__ == "__main__":
    student_dict = createDict()
    openGui(student_dict)
