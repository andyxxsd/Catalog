from flask import Flask, Blueprint, Response, request, abort, render_template, make_response, flash, redirect, url_for
from flask import session as login_session
from functools import wraps
import random, string
import json
import time
import hashlib
import requests
import urllib
import traceback
import utils
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from catalog import models

def json_response(message, status_code):
	resp = make_response(json.dumps(message), status_code)
	resp.headers['Content-Type'] = 'application/json'
	return resp

# Decoraters goes here
def require_login(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'email' not in login_session:
			flash('You need to login (Udacity criteria said)')
			return redirect('/')
		return f(*args, **kwargs)
	return decorated_function