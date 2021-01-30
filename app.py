import os

from flask import Flask, render_template, jsonify
import settings

project_dir = os.path.dirname(os.path.abspath(__file__))


# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(settings)
port = 5000

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Backend API works!'})


if __name__ == '__main__':
    app.run(port=port, debug=True)
