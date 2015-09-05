from flask import Flask, Blueprint, Response, request, abort, render_template, make_response, flash, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
import random, string
import json
import time
import hashlib
import requests
import urllib
import traceback
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import catalog.utils
from view import view
from test_api import test_api
from oauth_api import oauth_api
from data_api import data_api
from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
app.config.from_pyfile("config.py")

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = login_session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    return login_session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token    

BLUEPRINTS = [
	(test_api, ''),
	(view, ''),
	(oauth_api, ''),
	(data_api, ''),
]

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)
