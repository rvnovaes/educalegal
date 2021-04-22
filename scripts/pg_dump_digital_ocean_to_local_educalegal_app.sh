#!/bin/bash
export PGPASSFILE="/opt/educalegal/web/pgpass_do"
chmod 600 /opt/educalegal/web/pgpass_do
DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`
FILENAME=educa-legal-app-${DATE_WITH_TIME}.sql
pg_dump --host=educa-legal-producao-db-postgresql-do-user-8910843-0.b.db.ondigitalocean.com \
  --port=25060 \
  --dbname=educa-legal-app \
  --username=educa-legal-app \
  --no-password \
  --verbose \
  --clean > ${FILENAME}
PGPASSWORD=educalegal dropdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal createdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal psql -U educalegal -d educalegal -h localhost -e -p 7654 < ${FILENAME}
rm ${FILENAME}