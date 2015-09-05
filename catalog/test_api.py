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
import utils
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from catalog import models
from catalog.models.database_setup import Catalog, Base, Item

test_api = Blueprint('test', __name__)

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

@test_api.route("/add_data")
def add_data():
	models.test()
	return "OK"