#!/usr/bin/env bash
cd ..
# Does not erase tenant migration because it creates system tenant
rm audit/migrations/*.py
rm ged_configuration/migrations/*.py
rm person/migrations/*.py
rm users/migrations/*.py
find . -path "*/migrations/*.pyc"  -delete
rm db.sqlite3
#./manage.py makemigrations audit users ged_configuration person
#./manage.py migrate


