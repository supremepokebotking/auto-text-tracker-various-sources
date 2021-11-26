from burningalice.text_tracker import TextTracker
from burningalice.text_config_generator import TextConfigGenerator
from burningalice.metrics_tracker import MetricsTracker
from burningalice.metrics_tracker import METRIC_TYPES
from burningalice.map_analyzer import MapAnalyzer
from burningalice.auto_label_tracker import AutoLabelTracker

import json
import cv2
import numpy as np
from yolov3_manager import *
from pytesseract_manager import *

#https://coolors.co/afd2e9-9d96b8-9a7197-886176-7c5869

mapping_config = {
    'rows': 10,
    'cols': 10,
    'empty_cell_color': '#9D96B8',
    'color_mapping':
    {
        'abc': '#EAC435',
        'gravitas': '#345995',
        'lulua': '#03CEA4',
        'pokemon': '#FB4D3D',
        'ryza_1': '#CA1551',
        'ryza_2': '#7BE0AD',
        'smt_5': '#AEE5D8',
        'fox': '#E7E5E5',
        'three_kings': '#E5D0E3',
        'basic_stats_info': '#E0B0D5',
        'unique_words': '#AFD2E9',
    }
}

cell_data = [
    {
        'row': 1,
        'col': 1,
        'type': 'active_monster',
        'name': 'Pikachu',
        'is_json': True,
        'details': '{"stats":{"atk":254,"def":206,"spa":134,"spd":174,"spe":150}',
        'actions': ['Thunder', 'Thunder Wave', 'Thundershock', 'Agility', ],
    }
]

source_label_mappings = {
    "abc": ["abc_message_top", "abc_message_bottom"],
    "gravitas": ["gravitas_top", "gravitas_bottom"],
    "lulua": ["lulua_interrupt", "lulua_active_skill", "lulua_item"],
    "pokemon": ["pearl_message", "sword_message"],
    "ryza_1": ["ryza_1_enemy", "ryza_1_atk", "ryza_1_order_skill"],
    "ryza_2": ["ryza_2_order_skill", "ryza_2_atk", "ryza_2_enemy"],
    "smt_5": ["smt_5_atk"],
    "fox": ["fox_blue_bar", "fox_big_text"],
}


# METRICS STUFF
DEFAULT_METRICS_TRACKER =         {
            "total_messages_count": 0,
            "smt_5_messages":  [],# team_pokemon_id
            "abc_messages":[],
            "ryza_1_messages": [], #comma sep
            "ryza_2_messages": [], # comma sep
            "fox_messages": [], # comma sep
            "pokemon_messages": [], # comma sep
            "message_max_length": 0,
            "unique_words": [],
            "gravitas_messages": [],
            "lulua_messages": [],
            "messages_containing_three_letter_word": 0,
        }

generated_config = json.load(open("generated_text_config.json", "r"))

def get_labels(labels_path):
    return open(labels_path).read().strip().split("\n")


config = {}
labels = get_labels('yolo_v3/obj.names')

import uuid
session_id = uuid.uuid4()


frames_to_skip = 2
def process_framed_test_videos():
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture('Custom Vott Detector Video Clips.mp4')
    frame_num = 0

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video  file")

    # Read until video is completed
    while(cap.isOpened()):
        frame_num += 1

        # Capture frame-by-frame
        ret, frame = cap.read()
        for i in range(frames_to_skip):
            cap.read()
        if ret == True:

            labels_boxes = {}
            # Display the resulting frame

            original_filename = ('%d' % frame_num).zfill(5)
            original_filename = '%s.png' % original_filename
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
print('session_id', session_id)
