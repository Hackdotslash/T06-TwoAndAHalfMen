import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
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
        return render_template('nearby.html', res=None)
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
    if request.cookies.get('docID'):
        return redirect(url_for('doc_home'))
    return render_template('index.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor_reg():
    if request.cookies.get('docID'):
        return redirect(url_for('root'))

    if request.method == 'GET':
        return render_template('doctor-reg.html')
    else:
        # form ke values ko DB me daalo
        con = sqlite3.connect('newdb.db')
        name = request.form['name']
        phone = request.form['number']
        email = request.form['email']
        reg_no = request.form['reg_no']
        council = request.form['council']
        query = f"""
        insert into doctor values (NULL, "{name}", "{phone}", "{email}", "{reg_no}", "{council}", NULL, NULL, '')
        """
        print(query)
        with con:
            data = con.execute(query)
        query = f"""
        SELECT * FROM doctor ORDER BY ID DESC LIMIT 1
        """
        print(query)
        with con:
            data = con.execute(query)
        id = 1
        for row in data:
            id = row[0]
        # get ID of that doctor, next form me needed!
        return render_template('doctor-reg-2.html', docID = id)

@app.route('/docRegLocation', methods=['POST'])
def doc_reg_location():
    # ID, lat, lng aaega, push it to DB for given ID
    con = sqlite3.connect('newdb.db')
    id = request.form['id']
    lat = request.form['lat']
    lng = request.form['lng']
    query = f"""
    update doctor set latitude="{lat}", longitude="{lng}" where id="{id}"
    """
    print(query)
    with con:
        data = con.execute(query)
    
    response = make_response(redirect(url_for('doc_home')))
    response.set_cookie('docID', id, max_age=60*60*24*365)
    return response

@app.route('/docHome', methods=['GET'])
def doc_home():
    return render_template('doc_home.html')

@app.route('/logout', methods=['GET'])
def logout_doc():
    response = make_response(redirect(url_for('root')))
    response.set_cookie('docID', '3435', max_age=0)
    return response

@app.route('/new-blog', methods=['GET'])
def new_blog():
    return render_template('new-blog.html')

def get_doc_name(docID):
    # fix this
    return 'docName'

@app.route('/view-blogs', methods=['GET'])
def view_blogs():
    # get list of all blogs
    # (blog_id, title, author_id, published_at, content)
    blogs = [(1, 'blogTitle', 1, 'timestamp', 'blogContent'), (2, 'blogTitle2', 1, 'timestamp', 'blogContent')]
    length = len(blogs)
    for i in range(length):
        blogs[i] = list(blogs[i])
        blogs[i][2] = get_doc_name(blogs[i][2])

    return render_template('view-blogs.html', length = length, blogs = blogs)

@app.route('/view-blog/<id>')
def view_blog(id):
    # get stuff from blog table
    # get doc name from doc table using docID recvd from blog table
    doc_name = "dr. GB"
    title = "title"
    content = "content"
    return render_template('view-blog.html', title = title, content = content, author = doc_name)

@app.route('/submit-blog', methods=['POST'])
def submit_blog():
    docID = request.cookies.get('docID')
    # put stuff in the DB - blogID, title, content, docID
    # get ID
    blogID = 1
    return redirect(url_for('view_blog', id=blogID))

@app.route('/new-conference', methods=['GET'])
def new_conference():
    return render_template('new-conference.html')

@app.route('/view-conferences', methods=['GET'])
def view_conferences():
    # get list of all conferences
    # (id, zoom_link, title, desc, start, end, docID)
    conferences = [(1, 'https://us02web.zoom.us/j/2289', 'title', 'desc', 'timestamp_start', 'timestamp_end', 1), (2, 'https://us02web.zoom.us/j/8193', 'title2', 'desc2', 'timestamp_start', 'timestamp_end', 1)]
    length = len(conferences)
    for i in range(length):
        conferences[i] = list(conferences[i])
        conferences[i][6] = get_doc_name(conferences[i][6])

    return render_template('view-conferences.html', length = len(conferences), conferences = conferences)

@app.route('/submit-conference', methods=['POST'])
def submit_conference():
    docID = request.cookies.get('docID')
    # put stuff in the DB - confID, title, description, date, starttime, duration, docID
    return redirect(url_for('view_conferences'))

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
