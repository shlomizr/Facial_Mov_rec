#! /usr/bin/python

import tkinter as tk
import subprocess
import ctypes

# Function to perform face recognition with the provided user ID
def perform_face_recognition(user_id):
    # Run your face recognition script with the provided user ID
    # Replace 'face_recognition_script.py' with the actual name of your face recognition script
    subprocess.run(['python', 'face_recognition.py', user_id])

# Function to handle button click event
def open_face_recognition():
    user_id = user_id_entry.get()

    # Check if the user ID is valid (9 digits)
    if len(user_id) == 9 and user_id.isdigit():
        perform_face_recognition(user_id)
    else:
        result_label.config(text="Invalid User ID")

# Create the main window
window = tk.Tk()
window.title("Face Recognition")

# Calculate the center position of the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = 300
window_height = 150
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

# Set the window's position and size
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Set the font size
font_size = 12

# Create User ID label and entry
user_id_label = tk.Label(window, text="User ID (9 digits):", font=("Arial", font_size))
user_id_label.pack()

user_id_entry = tk.Entry(window, font=("Arial", font_size))
user_id_entry.pack()

# Create Open button
open_button = tk.Button(window, text="Open", command=open_face_recognition, font=("Arial", font_size))
open_button.pack()

# Create result label to display messages
result_label = tk.Label(window, text="", font=("Arial", font_size))
result_label.pack()

# Start the GUI event loop
window.mainloop()
