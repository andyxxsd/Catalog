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
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import utils
from test_api import test_api
from oauth_api import oauth_api
from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

from flask import current_app as app

view = Blueprint('view', __name__)

@view.context_processor
def get_catalogs():
	# login_session['uid'] = 1
	# login_session['email'] = '233@B.com'
	# login_session['picture'] = '/static/image/avatar.JPG'
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
		models.insert_catalog(login_session['uid'], request.form['name'])
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
			image = None
			if 'image' in request.files:
				image = store_image(request.files['image'])
			models.insert_item(login_session['uid'], request.form['name'], c, request.form['description'], image)
			flash('Successfully created a new item: ' + request.form['name'])
		else:
			flash('Catalog does not exist!')
		return redirect('/')
	else:
		return render_template('new_item.html',
			catalog=catalog)

@view.route("/catalogs/<catalog>/edit", methods=['GET', 'POST'])
@utils.require_login
def edit_catalog(catalog):
	if request.method == 'POST':
		c = models.select_catalog(catalog)
		if c is None:
			flash('Catalog does not exist!')
			return redirect('/')
		if c.created_user is None or c.created_user == login_session['uid']:
			models.update_catalog(c, request.form['name'])
			flash('Successfully updated catalog: ' + request.form['name'])
		else:
			flash('You are NOT authenticated to edit this catalog: ' + c.name)
		return redirect('/')
	else:
		c = models.select_catalog(catalog)
		if c.created_user is not None and c.created_user != login_session['uid']:
			flash('You are NOT authenticated to edit this catalog: ' + c.name)
			return redirect('/')
		return render_template('edit_catalog.html',
			catalog=models.select_catalog(catalog))

@view.route("/items/<id>/edit", methods=['GET', 'POST'])
@utils.require_login
def edit_item(id):
	if request.method == 'POST':
		item = models.select_item_by_id(id)
		if item is None:
			flash('Item does not exist!')
			return redirect('/')
		if item.created_user is None or item.created_user == login_session['uid']:
			image = None
			if 'image' in request.files:
				image = store_image(request.files['image'])
			models.update_item(item, request.form['name'], request.form['description'], image)
			flash('Successfully updated item: ' + request.form['name'])
		else:
			flash('You are NOT authenticated to edit this item: ' + item.name)
		return redirect('/')
	else:
		item = models.select_item_by_id(id)
		if item.created_user is not None and item.created_user != login_session['uid']:
			flash('You are NOT authenticated to edit this item: ' + item.name)
			return redirect('/')
		return render_template('edit_item.html',
			item=models.select_item_by_id(id))

@view.route("/catalogs/<catalog>/del", methods=['POST'])
@utils.require_login
def del_catalog(catalog):
	c = models.select_catalog(catalog)
	if c is None:
		flash('Catalog does not exist!')
		return redirect('/')
	if c.created_user is None or c.created_user == login_session['uid']:
		models.delete_catalog(c)
		flash('Successfully deleted catalog: ' + c.name)
	else:
		flash('You are NOT authenticated to delete this catalog: ' + c.name)
	return redirect('/')

@view.route("/items/<id>/del", methods=['POST'])
@utils.require_login
def del_item(id):
	item = models.select_item_by_id(id)
	if item is None:
		flash('Item does not exist!')
		return redirect('/')
	if item.created_user is None or item.created_user == login_session['uid']:
		models.delete_item(item)
		flash('Successfully deleted item: ' + item.name)
	else:
		flash('You are NOT authenticated to delete this item: ' + item.name)
	return redirect('/')

@view.route("/")
@view.route("/index")
def main_page():
	return render_template("index.html", 
		items=models.select_latest_items())

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def store_image(image):
	if image is None and not allowed_file(image.filename):
		return None
	filename = utils.random_string()+'.'+image.filename.rsplit('.', 1)[1]
	image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	return '/static/image/' + filename
