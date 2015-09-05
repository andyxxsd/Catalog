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

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
app.config.from_pyfile("config.py")

CLIENT_ID = json.loads(open('client_secrets.json').read())['web']['client_id']

test_api = Blueprint('test', __name__)
sql_api = Blueprint('sql', __name__)
view = Blueprint('view', __name__)

BLUEPRINTS = [
	(test_api, ''),
	(sql_api, ''),
	(view, '')
]

@app.context_processor
def get_catalogs():
	# login_session['email'] = '233@B.com'
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return dict(catalogs=models.select_catalogs(0, 0))




@test_api.route("/hello")
def hello():
	return "Hello World!"

@test_api.route("/demo")
def demo_page():
	return render_template("index_demo.html")

@test_api.route("/flash")
def test_flash():
	flash("YOLO")
	return render_template("index.html")

@sql_api.route("/rebuild")
def rebuild():
	models.rebuild()
	if app.debug:
		models.test()
	return Response("OK", 200)

@app.route("/gconnect", methods=['POST'])
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

	# url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	# result = json.loads(requests.get(url).text)
	# if result.get('error') is not None:
	# 	return utils.json_response(result.get('error'), 500)
	# gplus_id = credentials.id_token['sub']
	# if result['user_id'] != gplus_id:
	# 	return utils.json_response("Token's user ID doesn't match given user ID", 401)

	# Avoid duplicated login
	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		return utils.json_response('Current user is already connected', 200)
	login_session['access_token'] = access_token
	# login_session['gplus_id'] = gplus_id

	# Retrive user info for user
	userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
	answer = requests.get(userinfo_url, headers={'Authorization': 'Bearer '+ access_token})
	data = json.loads(answer.text)
	print(data)
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	# flash('you are now logged in as %s' % login_session['username'])
	print("here")
	return utils.json_response(login_session['email'], 200)

@view.route("/gdisconnect")
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		return utils.json_response("Current user not connected", 401)
	result = requests.get('https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token)
	if result.status_code == requests.codes.ok:
		del login_session['access_token']
		del login_session['email']
		del login_session['username']
		# del login_session['gplus_id']
	return utils.json_response('Successfully disconnected', 200)

@view.route("/catalogs/<catalog>")
def catalog_page(catalog):
	cid = models.select_cid_by_name(catalog)
	if cid is not None:
		return  render_template("catalog.html",
			catalog=catalog,
			items=models.select_items_by_cid(cid, 0, 10))
	else:
		abort(404)

@view.route("/items/<id>")
def item_page(id):
	item = models.select_item_by_id(id)
	print(item)
	if item is not None:
		return render_template("item.html",
			item=item)
	else:
		abort(404)

@view.route("/catalogs/new", methods=['GET', 'POST'])
@utils.require_login
def new_catalog():
	if request.method == 'POST':
		models.insert_catalog(request.form['name'])
		flash('Successfully created a new catalog: ' + request.form['name'])
		return redirect('/')
	else:
		return render_template('new_catalog.html')

@view.route("/catalogs/<catalog>/new", methods=['GET', 'POST'])
@utils.require_login
def new_item(catalog):
	if request.method == 'POST':
		cid = models.select_cid_by_name(catalog)
		if cid is not None:
			models.insert_item(request.form['name'], cid, request.form['description'])
			flash('Successfully created a new item: ' + request.form['name'])
		else:
			flash('Catalog does not exist!')
		return redirect('/')
	else:
		return render_template('new_item.html',
			catalog=catalog)

@view.route("/catalogs/<catalog>/del")
@utils.require_login
def del_catalog(catalog):
	cid = models.select_cid_by_name(catalog)
	if cid is not None:
		models.delete_catalog(cid)
		flash('Successfully deleted catalog: ' + catalog)
	else:
		flash('Catalog does not exist!')
	return redirect('/')

@view.route("/items/<id>/del")
@utils.require_login
def del_item(id):
	item = models.select_item_by_id(id)
	if item is not None:
		models.delete_item(id)
		flash('Successfully deleted item: ' + item['name'])
	else:
		flash('Item does not exist!')
	return redirect('/')

@view.route("/")
@view.route("/index")
def main_page():
	return render_template("index.html", 
		items=models.select_latest_items(0, 10))

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)
