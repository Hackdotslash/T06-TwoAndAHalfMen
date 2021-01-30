import os
from flask import Flask, render_template, jsonify, request
import settings
import requests
import hmac
import base64
import json

project_dir = os.path.dirname(os.path.abspath(__file__))


# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(settings)
port = 5000

with open('symptoms.json') as f:
    symptoms = json.load(f)


@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Backend API works!'})

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
        'year_of_birth': args['year_of_birth'][0],
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
