#!/usr/bin/env python

from catalog import app
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--setup', help='Set up the database for this web app', action="store_true")
parser.add_argument('-t', '--test', help='Add some test data', action="store_true")
parser.parse_args()
args = parser.parse_args()

if args.setup:
	from catalog.models import database_setup

if args.test:
	from catalog import models
	models.test()

if not args.setup and not args.test:
	if __name__ == "__main__":
		app.run(host="0.0.0.0", port=8000, debug=True)
