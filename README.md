##Enviroment

	python2 ONLY, flask, sqlalchemy

##Requirement

	To use Google oauth API, you need to apply for an Google oauth credential.
	Then download the json file on the detail page.
	Rename it as: client_secrets.json
	PS. I left mine.

##Installation

	1. Install python2 (https://www.python.org/downloads/)
	2. Install flask & sqlalchemy

		pip install flask, sqlalchemy

	3. Run applicant.py to start the server

##Testing

	Request the /add_data api, it will automaticlly generate some data

##Cleanning

	./applicant.py --clean

##Project Criteria

	1. Implements api endpoint XML.
	2. Support image CRUD for Items.
	3. Protect website from CSRF.
