# Flask app that just reads and services a single json file



from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json

import os

DEBUG = bool(int(os.environ.get('DEBUG', 1)))
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5114))
THREADED = bool(int(os.environ.get('THREADED', 1)))


app = Flask(__name__)
CORS(app)

map_filename = './map_data.json'


mapping_config = {
    'rows': 10,
    'cols': 10,
    'empty_cell_color': '#ff00ff',
    'color_mapping':
    {
        'active_monster': '#ff00fc',
        'enemy_active_monster': '#fa00ff',
        'active_stats_modifier_monster': '#ff00ff',
        'enemy_active_stats_modifier_monster': '#ff00ff',
        'p1_field': '#ff00ff',
        'p2_field': '#ff00ff',
    }
}

cell_data_1 = {
        'row': 1,
        'col': 1,
        'is_json': True,
        'type': 'active_monster',
        'name': 'Pikachu',
        'details': '"stats":{"atk":254,"def":206,"spa":134,"spd":174,"spe":150}',
        'actions': ['Thunder', 'Thunder Wave', 'Thundershock', 'Agility', ],
    }


cell_data_2 = {
        'row': 1,
        'col': 1,
        'type': 'enemy_active_monster',
        'name': 'Pikachu',
        'details': '"stats":{"atk":254,"def":206,"spa":134,"spd":174,"spe":150}',
        'actions': ['Thunder', 'Thunder Wave', 'Thundershock', 'Agility', ],
    }



# route http posts to this method
@app.route('/api/get_test_map_data', methods=['POST'])
def search_single_phrase():

    return Response(response=json.dumps({'mapping_config': mapping_config, 'cell_data': [cell_data_1, cell_data_2]}), status=200,mimetype="application/json")



# route http posts to this method
@app.route('/api/get_map_data', methods=['POST'])
def search_basic_multi_query():

    return Response(response=json.dumps(json.load(open(map_filename))), status=200,mimetype="application/json")


# start flask app
if __name__ == '__main__':
    app.run(debug=DEBUG, port=FLASK_PORT, host='0.0.0.0', threaded=THREADED)
