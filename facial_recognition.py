#! /usr/bin/python

import cv2
import imutils
import pickle
import time
import face_recognition
from imutils.video import VideoStream
from imutils.video import FPS

print("[INFO] Starting facial recognition...")

encodings_file = "encodings.pickle"

# Load the known faces and encodings
print("[INFO] Loading encodings...")
data = pickle.loads(open(encodings_file, "rb").read())

# Initialize video stream and allow the camera to warm up
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Initialize the FPS counter
fps = FPS().start()

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

            # Determine the recognized face with the highest vote count
            name = max(counts, key=counts.get)

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

# Stop the FPS counter and display information
fps.stop()
print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approximate FPS: {:.2f}".format(fps.fps()))

# Cleanup
cv2.destroyAllWindows()
vs.stop()