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
    "abc": ["abc_message"],
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


def text_detected_callback(label, rect, ocr_config, ocr_key):
    print(label, ocr_key)

#    actual_message = "cat"
    actual_message = parse_rect_with_pytesseract_config(rect, ocr_config)
    actual_message = actual_message["result"]

    print(actual_message)
    # get source metrics
    metrics_source_name = None
    for source_name in source_label_mappings:
        if label in source_label_mappings[source_name]:
            metrics_source_name = source_name
            break

    if metrics_source_name is not None:
        metrics_tracker.update_metrics(metrics_source_name, 'messages', actual_message, METRIC_TYPES.APPEND)

    metrics_tracker.update_metrics(None, 'total_messages_count', None, METRIC_TYPES.INCREMENT)
    metrics_tracker.update_metrics(None, 'message_max_length', len(actual_message), METRIC_TYPES.MAX)

    did_see_three_letter_word = False
    for word in actual_message.split(' '):
        metrics_tracker.update_metrics(None, 'unique_words', word, METRIC_TYPES.ADD_IF_DOESNT_EXIST)
        if not did_see_three_letter_word:
            if len(word) == 3:
                did_see_three_letter_word = True
                metrics_tracker.update_metrics(None, 'messages_containing_three_letter_word', None, METRIC_TYPES.INCREMENT)

config = {}
labels = get_labels('yolo_v3/obj.names')

import uuid
session_id = uuid.uuid4()

autolabeler = AutoLabelTracker(config, labels, session_id)
textTracker = TextTracker(generated_config, text_detected_callback)
metrics_tracker = MetricsTracker(DEFAULT_METRICS_TRACKER)
map_analyzer = MapAnalyzer(mapping_config)


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

def generate_map_analysis_data():
    messages_cells = []
    for source_name in source_label_mappings:
        last_message = ""
        messages_for_source = metrics_tracker.tracking_metrics["%s_messages" % source_name]
        if len(messages_for_source) > 0:
            last_message = messages_for_source[-1]

        messages_cells.append({
            'row': 1,
            'col': 1,
            'type': source_name,
            'name': source_name,
            'is_json': False,
            'details': "# Number of processed messages: %d\nLast Message: %s" % (len(messages_for_source), last_message),
            'actions': ['Translate to Chinese', 'Search with bing!'],
        })

    # stats information: total count, max length, messages containing 3 letter words
    messages_cells.append({
        'row': 1,
        'col': 1,
        'type': "basic_stats_info",
        'name': "Basic Stats",
        'is_json': False,
        'details': "total_messages_count: %d, message_max_length: %d, messages_containing_three_letter_word: %d" % (metrics_tracker.tracking_metrics["total_messages_count"], metrics_tracker.tracking_metrics["message_max_length"], metrics_tracker.tracking_metrics["messages_containing_three_letter_word"], ),
    })

    # sources that contain a three letter word
    sources_with_three_letter_words = set()
    for source_name in source_label_mappings:
        messages_for_source = metrics_tracker.tracking_metrics["%s_messages" % source_name]
        for message in messages_for_source:
            for word in message.split(' '):
                 if len(word) == 3:
                     sources_with_three_letter_words.add(source_name)
                     break

    if len(sources_with_three_letter_words) > 0:
        messages_cells.append({
            'row': 1,
            'col': 1,
            'type': "three_kings",
            'name': "Sources with 3 letter words",
            'is_json': False,
            'details': "These sources have provided a word with 3 letters: %s" % (list(sources_with_three_letter_words) ),
        })

    map_ana_data = {'mapping_config': mapping_config, 'cell_data': messages_cells}
    json.dump(map_ana_data, open("map_data.json", 'w'))


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

            image_with_labels, labels_boxes = predict_image(frame)
            updated_labels, assisted_labels = textTracker.process_frame("keyoo", frame, labels_boxes)
            if len(assisted_labels) > 0:
                print('assisted_labels', assisted_labels)

            original_filename = ('%d' % frame_num).zfill(5)
            original_filename = '%s.png' % original_filename
            cv2.imshow('Frame', image_with_labels)

            autolabeler.store_frame(original_filename, frame, updated_labels, assisted_labels)
            generate_map_analysis_data()

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            # Break the loop
        else:
            break

    # When everything done, release
    # the video capture object
    cap.release()
    autolabeler.wrapup()

    # Closes all the frames
    cv2.destroyAllWindows()


process_framed_test_videos()
print('session_id', session_id)
