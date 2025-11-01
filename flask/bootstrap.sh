#!/bin/sh
export FLASK_APP=./users_rest/index.py
pipenv run flask --debug run -h 0.0.0.0