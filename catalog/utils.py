from flask import make_response, redirect, flash
from flask import session as login_session
from functools import wraps
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import json

def json_response(message, status_code):
	resp = make_response(json.dumps(message), status_code)
	resp.headers['Content-Type'] = 'application/json'
	return resp

def xml_response(message, status_code):
	resp = make_response(ET.tostring(message), status_code)
	resp.headers['Content-Type'] = 'application/xml'
	return resp

def dict_to_xml(tag, d):
	'''
	Turn a simple dict of key/value pairs into XML
	'''
	tree = Element(tag)
	for key, val in d.items():
		child = Element(key)
		child.text = str(val)
		tree.append(child)
	return tree

def list_to_xml(tag, l):
	'''
	Turn a list of xml into XML
	'''
	tree = Element(tag)
	for val in l:
		tree.append(val)
	return tree

def require_login(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'email' not in login_session:
			flash('You need to login (Udacity criteria said)')
			return redirect('/')
		return f(*args, **kwargs)
	return decorated_function
