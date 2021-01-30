"""Settings configuration - Configuration for environment variables can go in here."""

import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv('FLASK_ENV', default='production')
DEBUG = ENV == 'development'
DIAGNOSIS_TOKEN = os.getenv('DIAGNOSIS_TOKEN', default='null')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY', default='octocat')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
SQLALCHEMY_TRACK_MODIFICATIONS = False
