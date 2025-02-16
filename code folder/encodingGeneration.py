import dlib
import os
import cv2
import json
import numpy as np

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("dependencey/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("dependencey/dlib_face_recognition_resnet_model_v1.dat")


def generatefacedata(imgpath, encodingPath):
    encodings = []
    encoddatas = []

    def get_face_encodings(img):
        # Detect faces
        detect_face = detector(img, 1)
        face_encodings = []

        for face in detect_face:
            # Get facial landmarks and compute face descriptor
            shape = predictor(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), face)
            face_encoding = np.array(facerec.compute_face_descriptor(img, shape))
            print(face_encoding)
            face_encodings.append(face_encoding)
        print(face_encodings)
        return face_encodings

    # Check if the folder exists and has images
    print(f"Image path: {imgpath}")
    if not os.path.exists(imgpath):
        raise FileNotFoundError(f"The folder {imgpath} does not exist.")
    
    image_files = [img for img in os.listdir(imgpath) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print("No images found in the provided folder.")
        return

    # Process each image in the folder
    for img_name in image_files:
        print(f"Processing image: {img_name}")
        img_path = os.path.join(imgpath, img_name)
        photo = cv2.imread(img_path)

        if photo is None:
            print(f"Failed to load image: {img_name}")
            continue

        encod = get_face_encodings(photo)
        encodings.extend(encod)
        print(encodings)

    # Read existing encodings if the file exists and is not empty
    if os.path.exists(encodingPath):
        if os.path.getsize(encodingPath) > 0:
            with open(encodingPath, 'r') as file:
                try:
                    encoddatas = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {encodingPath}. Starting fresh.")
                    encoddatas = []
        else:
            print(f"File {encodingPath} is empty. Starting fresh.")
            encoddatas = []

    # Append new encodings
    for encoding in encodings:
        encoddatas.append(encoding.tolist())

    # Save updated encodings back to the file
    with open(encodingPath, 'w') as file:
        json.dump(encoddatas, file, indent=4)
    
    print(f"Encodings successfully saved to {encodingPath}.")



imgpath ='trainingdata'
encodingpth = 'trainingdata'
generatefacedata(imgpath=imgpath,encodingPath=encodingpth)