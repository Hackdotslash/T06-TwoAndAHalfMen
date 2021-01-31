import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
import settings
import requests
import hmac
import base64
import json
import sqlite3
import time
import datetime
from flask_cors import CORS, cross_origin

project_dir = os.path.dirname(os.path.abspath(__file__))

def send_email(sender_email_id, sender_email_id_password, receiver_email_id, message):
    # Python code to illustrate Sending mail from
    # your Gmail account
    import smtplib, ssl

    # creates SMTP session
    # s = smtplib.SMTP('smtp.gmail.com', 587)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        # start TLS for security
        # s.starttls()

        # Authentication
        s.login(sender_email_id, sender_email_id_password)
        # sending the mail
        s.sendmail(sender_email_id, receiver_email_id, message)

    # terminating the session
    # s.quit()

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
        lat, lon = doc[6], doc[7]
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
    con = sqlite3.connect('newdb.db')
    query = f"""
    SELECT name FROM doctor where id={int(docID)}
    """
    print(query)
    with con:
        data = con.execute(query)
    for row in data:
        return row[0]

@app.route('/view-blogs', methods=['GET'])
def view_blogs():
    # get list of all blogs
    # (blog_id, title, author_id, published_at, content)
    blogs = []
    con = sqlite3.connect('newdb.db')
    query = f"""
    SELECT * FROM blogpost
    """
    print(query)
    with con:
        data = con.execute(query)
    for row in data:
        blogs.append(row)

    print(blogs)
    length = len(blogs)
    for i in range(length):
        blogs[i] = list(blogs[i])
        blogs[i][2] = get_doc_name(blogs[i][2])

    return render_template('view-blogs.html', length = length, blogs = blogs)

@app.route('/view-blog/<id>')
def view_blog(id):
    # get stuff from blog table
    con = sqlite3.connect('newdb.db')
    query = f"""
    SELECT * FROM blogpost where blog_id={int(id)}
    """
    print(query)
    blog = []
    with con:
        data = con.execute(query)
    for row in data:
        blog = tuple(row)
    # get doc name from doc table using docID recvd from blog table
    doc_name = "dr. GB"
    title = blog[1]
    content = blog[4]
    return render_template('view-blog.html', title = title, content = content, author = doc_name)

@app.route('/submit-blog', methods=['POST'])
def submit_blog():
    docID = request.cookies.get('docID')
    # put stuff in the DB - blogID, title, content, docID
    con = sqlite3.connect('newdb.db')
    title = request.form['title']
    content = request.form['content']
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    query = f"""
    insert into blogpost values (NULL, "{title}", "{docID}", "{timestamp}", "{content}")
    """
    print(query)
    with con:
        data = con.execute(query)
    query = f"""
    SELECT * FROM blogpost ORDER BY ID DESC LIMIT 1
    """
    print(query)
    with con:
        data = con.execute(query)
    blogID = 1
    for row in data:
        blogID = row[0]    # get ID
    return redirect(url_for('view_blog', id=blogID))

@app.route('/share-symptoms', methods=['POST'])
def send_mail():
    age = request.cookies.get('age')
    gender = request.cookies.get('gender')
    symptoms = request.cookies.get('symptoms')
    con = sqlite3.connect('newdb.db')
    def execute(query):
        with con:
            data = con.execute(query)
        return data
    print(request.json)
    doc_email = list(execute('select email from doctor where id={}'.format(request.json['doctorId'])))[0][0]
    message = """
        Hi, patient has shared symptoms with you
        Age: {}
        Gender: {}
        Symptoms: {}
    """.format(age, gender, symptoms)
    print(message)
    send_email("bonvoyage6566@gmail.com", "1711065and66", doc_email, message)
    return jsonify({'status': True});


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
    # return jsonify({'data': res})
    response = make_response(render_template('diagnosis_result.html', res=res))
    response.set_cookie('gender', str(args['gender'][0]), max_age=60*60*24*365)
    response.set_cookie('age', str(args['age'][0]), max_age=60*60*24*365)
    response.set_cookie('symptoms', str(res), max_age=60*60*24*365)
    return response


if __name__ == '__main__':
    app.run(port=port, debug=True)
