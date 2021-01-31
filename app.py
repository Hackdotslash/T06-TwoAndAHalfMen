import os
from flask import Flask, render_template, jsonify, request
import settings
import requests
import hmac
import base64
import json
import sqlite3

project_dir = os.path.dirname(os.path.abspath(__file__))


# create and configure the app
app = Flask(__name__, instance_relative_config=True)
# con = sqlite3.connect('newdb.db')
app.config.from_object(settings)
port = 5000

with open('symptoms.json') as f:
    symptoms = json.load(f)

@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    if request.method == 'GET':
        return render_template('nearby.html', res=None)
    # dummy = [(19.116884428986182, 72.93164483021962), (19.10123794041552, 72.91207824204169)]
    # print('request data',request.json)
    con = sqlite3.connect('newdb.db')
    def execute(query):
        with con:
            data = con.execute(query)
        return data

    user_lat, user_lon = [request.json[i] for i in ['latitude', 'longitude']]
    api_key = app.config['MAPS_API_KEY']
    url = 'https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=600x300&center={},{}&zoom=13&size=600x300&maptype=roadmap&markers=color:red|label:D'.format(user_lat, user_lon, api_key)
    docs = []
    for doc in execute('select * from doctor;'): # list(query_res):
        print('inside loop',doc)
        lat, lon = doc[5], doc[6]
        docs.append(doc)
        url += '|{},{}'.format(lat,lon)
    url += '&markers=color:blue|label:I|{},{}'.format(user_lat, user_lon)
    url += '&key={}'.format(api_key)
    print(url)
    res = requests.get(url)
    print(docs)
    return render_template('nearby.html', res = base64.b64encode(res.content).decode(), doctors = docs)


@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

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
    if data == 'Invalid token':
        return jsonify({'data': ['Influenza', 'Common cold']})
    res = []
    for i in range(min(3, len(data))):
        # if data[i]['Issue']['Accuracy'] >= 50:
        res.append(data[i]['Issue']['ProfName'])
    print(res)
    # return jsonify({'data': res})
    return render_template('diagnosis_result.html', res=res)


if __name__ == '__main__':
    app.run(port=port, debug=True)
