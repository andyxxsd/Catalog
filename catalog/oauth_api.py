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

import utils
from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

oauth_api = Blueprint('oauth_api', __name__)

@oauth_api.route("/gconnect", methods=['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		return utils.json_response('Invalid state', 401)
	code = request.data

	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		return utils.json_response('Failed to upgrade the authorization code', 401)
	access_token = credentials.access_token

	# Avoid duplicated login
	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		return utils.json_response('Current user is already connected', 200)
	login_session['access_token'] = access_token

	# Retrive user info for user
	userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
	answer = requests.get(userinfo_url, headers={'Authorization': 'Bearer '+ access_token})
	data = json.loads(answer.text)
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	flash('You are now logged in as %s' % login_session['email'])
	return utils.json_response(login_session['email'], 200)

@oauth_api.route("/gdisconnect")
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		return utils.json_response("Current user not connected", 401)
	result = requests.get('https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token)
	if result.status_code == requests.codes.ok:
		del login_session['access_token']
		del login_session['email']
	return utils.json_response('Successfully disconnected', 200)
