#!/usr/bin/env python

from catalog import app
import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--setup', help='Set up the database for this web app', action="store_true")
parser.add_argument('-t', '--test', help='Add some test data', action="store_true")
parser.add_argument('-c', '--clean', help='Delete cache files & all the stored images', action="store_true")
parser.parse_args()
args = parser.parse_args()

if args.setup:
	from catalog.models import database_setup

if args.test:
	from catalog import models
	models.test()

if args.clean:
	os.system("find ./catalog/static/image -type f -not -name 'avatar.JPG' | xargs rm")
	os.system("find . -type f -name '*.pyc' | xargs rm")
	os.system("find . -type d -name '__pycache__' | xargs rm -r")
	os.system("rm catalog.db")

if not args.setup and not args.test and not args.clean:
	if __name__ == "__main__":
		app.run(host="0.0.0.0", port=8000, debug=True)
