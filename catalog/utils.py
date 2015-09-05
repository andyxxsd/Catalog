from flask import make_response, redirect, flash
from flask import session as login_session
from functools import wraps
import json

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