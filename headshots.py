#! /usr/bin/python

import cv2

name = 'Shlomi'  # Replace with your name

cam = cv2.VideoCapture(0)  # Use index 0 for the default camera

cv2.namedWindow("Capture Images", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Capture Images", 500, 400)

img_counter = 0
capture_mode = False

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        break

    if capture_mode:
        cv2.putText(frame, "Press SPACE to capture (ESC to exit)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Press C to start capturing (ESC to exit)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Capture Images", frame)

    k = cv2.waitKey(1)
    if k == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k == ord('c') or k == ord('C'):
        # C pressed
        capture_mode = not capture_mode
    elif k == 32 and capture_mode:
        # SPACE pressed
        img_name = "dataset/" + name + "/image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()
cv2.destroyAllWindows()
