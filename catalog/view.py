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
from test_api import test_api
from oauth_api import oauth_api
from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

view = Blueprint('view', __name__)

@view.context_processor
def get_catalogs():
	# login_session['email'] = '233@B.com'
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	print(models.select_catalogs())
	return dict(catalogs=models.select_catalogs())

@view.route("/catalogs/<catalog>")
def catalog_page(catalog):
	c = models.select_catalog(catalog)
	if c is not None:
		return  render_template("catalog.html",
			catalog=catalog,
			items=models.select_items_by_catalog(c))
	else:
		abort(404)

@view.route("/items/<id>")
def item_page(id):
	item = models.select_item_by_id(id)
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
		c = models.select_catalog(catalog)
		if c is not None:
			models.insert_item(request.form['name'], c, request.form['description'])
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
	c = models.select_catalog(catalog)
	if c is not None:
		models.delete_catalog(c)
		flash('Successfully deleted catalog: ' + c.name)
	else:
		flash('Catalog does not exist!')
	return redirect('/')

@view.route("/items/<id>/del")
@utils.require_login
def del_item(id):
	item = models.select_item_by_id(id)
	if item is not None:
		models.delete_item(item)
		flash('Successfully deleted item: ' + item.name)
	else:
		flash('Item does not exist!')
	return redirect('/')

@view.route("/")
@view.route("/index")
def main_page():
	return render_template("index.html", 
		items=models.select_latest_items())
