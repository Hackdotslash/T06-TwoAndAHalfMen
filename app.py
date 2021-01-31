import os
from flask import Flask, render_template, jsonify, request
import settings
import requests
import hmac
import base64
import json
import sqlite3
from flask_cors import CORS, cross_origin

project_dir = os.path.dirname(os.path.abspath(__file__))


# create and configure the app
app = Flask(__name__, instance_relative_config=True)
cors = CORS(app)
# con = sqlite3.connect('newdb.db')
app.config.from_object(settings)
port = 5000

with open('symptoms.json') as f:
    symptoms = json.load(f)

@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    if request.method == 'GET':
        return render_template('nearby.html')
    # dummy = [(19.116884428986182, 72.93164483021962), (19.10123794041552, 72.91207824204169)]
    # print('request data',request.json)
    con = sqlite3.connect('newdb.db')
    def execute(query):
        with con:
            data = con.execute(query)
        return data
    # query_res = execute('select latitude,longitude from doctor;')
    # for lat, lon in list(query_res):
        # tempstri += '|{},{}'.format(lat, lon)
    user_lat, user_lon = [request.json[i] for i in ['latitude', 'longitude']]
    api_key = app.config['MAPS_API_KEY']
    url = 'https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=600x300&center={},{}&zoom=13&size=600x300&maptype=roadmap&markers=color:red|label:D'.format(user_lat, user_lon, api_key)
    # print('db query_res:',list(query_res), tempstri)
    for lat, lon in execute('select latitude,longitude from doctor;'): # list(query_res):
        print('inside loop',lat, lon)
        url += '|{},{}'.format(lat,lon)
    url += '&markers=color:blue|label:I|{},{}'.format(user_lat, user_lon)
    url += '&key={}'.format(api_key)
    print(url)
    res = requests.get(url)
    return base64.b64encode(res.content).decode()


@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor_reg():
    if request.method == 'GET':
        return render_template('doctor-reg.html')
    else:
        # form ke values ko DB me daalo
        # get ID of that doctor, next form me needed!
        id = 1
        return render_template('doctor-reg-2.html', docID = id)


@app.route('/docRegLocation', methods=['POST'])
def doc_reg_location():
    # ID, lat, lng aaega, push it to DB for given ID
    return render_template('doc_home.html')

@app.route('/diagnosis', methods=['GET'])
def diagnosis():
    url = 'https://sandbox-healthservice.priaid.ch/diagnosis'
    token = app.config['DIAGNOSIS_TOKEN']
    print(token)
    args = dict(request.args.lists())
    # return jsonify({'a':'b'})
    symptom_list = args['symptoms']
    print(symptom_list)
    symptom_ids = []
    for symptom in symptom_list:
        if symptoms.get(symptom.lower()):
            symptom_ids.append(symptoms[symptom.lower()])
    symptom_ids = '[{}]'.format(','.join(map(str, symptom_ids)))
    print(symptom_ids)
    data = {
        'token': token,
        'language': 'en-gb',
        'symptoms': symptom_ids,
        'gender': args['gender'][0],
        'year_of_birth': 2021 - int(args['age'][0]),
        'format': 'json'
    }
    res = requests.get(url, data)
    # return jsonify({'text':res.text, 'status':res.status_code})
    data = eval(res.text)
    print('response',data)
    res = []
    for i in range(min(3, len(data))):
        # if data[i]['Issue']['Accuracy'] >= 50:
        res.append(data[i]['Issue']['ProfName'])
    print(res)
    return jsonify({'data': res})


if __name__ == '__main__':
    app.run(port=port, debug=True)
