import config
import os
import flask 
from flask import request, jsonify, make_response
import sqlite3
from sqlite3 import Error
from datetime import datetime
import polling
import requests
import json
import time
import threading

app = flask.Flask(__name__)

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Default page
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Inkbird Brewfather bridge API</h1><p>An API for getting temperatures from Inkbird ITC-308 WiFi and .</p>'''

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# A route to return all temperatures
@app.route('/api/v1/resources/temperatures/all', methods=['GET'])
def api_all():
    conn = create_connection(config.db_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    temperatures = cur.execute('SELECT * FROM temperatures;').fetchall()    
    return jsonify(temperatures)

# A route to return all temperatures
@app.route('/api/v1/resources/temperatures/latest', methods=['GET'])
def api_latest():
    conn = create_connection(config.db_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    temperatures = cur.execute('SELECT * FROM temperatures order by measuredatetime desc limit 1;').fetchall()    
    return jsonify(temperatures)

@app.route('/api/v1/resources/temperatures', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    measuredatetime = query_parameters.get('measuredatetime')
    temperature = query_parameters.get('temperature')

    query = "SELECT * FROM temperatures WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if measuredatetime:
        query += ' measuredatetime=? AND'
        to_filter.append(measuredatetime)
    if temperature:
        query += ' temperature=? AND'
        to_filter.append(temperature)
    if not (id or measuredatetime or temperature):
        return not_found(404)

    query = query[:-4] + ';'

    conn = create_connection(config.db_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results) 

@app.route('/api/v1/resources/temperatures', methods=['POST'])
def insert_temperature():
    if not request.json or not 'temperature' or not 'measuredatetime' in request.json:
        return not_found(400)  
    else:  
        conn = create_connection(config.db_file)
        query = "SELECT id FROM temperatures ORDER BY ID desc LIMIT 1"
        conn.row_factory = dict_factory
        cur = conn.cursor()
        newid = cur.execute(query).fetchone()['id'] + 1
        
        temperatures = {
            'id': newid, 
            'measuredatetime': request.json['measuredatetime'], #datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            'temperature': request.json['temperature']             
        }

        #insert into db here
        cur.execute("insert into temperatures(id, measuredatetime, temperature) values(?,?,?)", (newid, request.json['measuredatetime'], request.json['temperature']))
        conn.commit()       

        return jsonify(temperatures), 201 

def upload_brewfather(temperature):
    brewfather = {        
            'name': "Inkbird", #Required field, this will be the ID in Brewfather  
            'aux_temp': temperature, #Fridge Temp 
            'temp_unit': "C", # C, F, K       
    }
    url = config.post_url    
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(brewfather), headers=headers)
    return r

def upload_loop():
    t=0
    while True:        
        t = t + 1
        print("Thread has run", t, "times and runs every", config.upload_frequency, "seconds. Current time:", datetime.now().strftime("%d-%m-%Y, %H:%M:%S")) 
        #get latest from Inkbird
        #insert in DB
        #upload to brewfather
        #upload_brewfather(20)
        time.sleep(config.upload_frequency)

if __name__ == '__main__':    
    monitoring_thread = threading.Thread(target = upload_loop)
    monitoring_thread.start()
    app.run()     