#!/bin/sh
docker stop db
docker start db
sleep 3
PGPASSWORD=educalegal dropdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal createdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal psql -hlocalhost -Ueducalegal -p7654 -deducalegal -f/opt/bkp/el.sql
