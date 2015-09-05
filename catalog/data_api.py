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
import xml.etree.ElementTree as ET

import utils
from test_api import test_api
from oauth_api import oauth_api
from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

data_api = Blueprint('data_api', __name__)

# JSON API
@data_api.route('/catalogs.json')
def catalogs_json():
	'''
		Since the object is not JSON serializable.
		We could firstly convert it to a dict.
		Then a list of dict which is JSON serializable.
	'''
	return utils.json_response([ x.serialize for x in models.select_catalogs_all() ], 200)

@data_api.route('/items.json')
def items_json():
	return utils.json_response([ x.serialize for x in models.select_items_all() ], 200)

@data_api.route("/catalogs/<catalog>.json")
def catalog_json(catalog):
	c = models.select_catalog(catalog)
	if c is not None:
		return utils.json_response(c.serialize, 200)
	else:
		abort(404)

@data_api.route("/items/<id>.json")
def item_json(id):
	item = models.select_item_by_id(id)
	if item is not None:
		return utils.json_response(item.serialize, 200)
	else:
		abort(404)

# XML API
@data_api.route('/catalogs.xml')
def catalogs_xml():
	'''
		Convert list of unserializable object to xml:
		1. Retrive data
		2. Turn each object to xml
		3. Wrap them with a xml tag
	'''
	return utils.xml_response(utils.list_to_xml('catalogs',
		[ utils.dict_to_xml('catalog', x.serialize) for x in models.select_catalogs_all() ]), 200)

@data_api.route('/items.xml')
def items_xml():
	return utils.xml_response(utils.list_to_xml('items',
		[ utils.dict_to_xml('item', x.serialize) for x in models.select_items_all() ]), 200)

@data_api.route("/catalogs/<catalog>.xml")
def catalog_xml(catalog):
	c = models.select_catalog(catalog)
	if c is not None:
		return utils.xml_response(utils.dict_to_xml('catalog', c.serialize), 200)
	else:
		abort(404)

@data_api.route("/items/<id>.xml")
def item_xml(id):
	item = models.select_item_by_id(id)
	if item is not None:
		return utils.xml_response(utils.dict_to_xml('item', item.serialize), 200)
	else:
		abort(404)
