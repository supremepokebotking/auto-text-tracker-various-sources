from burningalice.text_tracker import TextTracker
from burningalice.text_config_generator import TextConfigGenerator
from burningalice.metrics_tracker import MetricsTracker
from burningalice.metrics_tracker import METRIC_TYPES
from burningalice.map_analyzer import MapAnalyzer
from burningalice.auto_label_tracker import AutoLabelTracker

import json
import cv2
import numpy as np
from pytesseract_manager import *

#https://coolors.co/afd2e9-9d96b8-9a7197-886176-7c5869

generated_config = json.load(open("generated_text_config.json", "r"))

def text_detected_callback(label, rect, ocr_config, ocr_key):
#    print(label, ocr_config)
    print(label, ocr_key)
    actual_message = parse_rect_with_pytesseract_config(rect, ocr_config)
    actual_message = actual_message["result"]
    print('actual_message', actual_message)

textTracker = TextTracker(generated_config, text_detected_callback)
frames_to_skip = 2

def process_framed_test_videos():
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture('Custom Vott Detector Video Clips.mp4')

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video  file")

    # Read until video is completed
    while(cap.isOpened()):

        # Capture frame-by-frame
        ret, frame = cap.read()

        for i in range(frames_to_skip):
            cap.read()
        if ret == True:

            labels_boxes = {}
            # Display the resulting frame
            updated_labels, assisted_labels = textTracker.process_frame("keyoo", frame, labels_boxes)
            if len(assisted_labels) > 0:
                print('assisted_labels', assisted_labels)

            cv2.imshow('Frame', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            # Break the loop
        else:
            break

    # When everything done, release
    # the video capture object
    cap.release()

# Closes all the frames
cv2.destroyAllWindows()

process_framed_test_videos()
