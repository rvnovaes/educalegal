#!/bin/bash
export PGPASSFILE="/opt/educalegal/web/pgpass_do_test"
chmod 600 /opt/educalegal/web/pgpass_do_test
DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`
FILENAME=educa-legal-app-${DATE_WITH_TIME}.sql
pg_dump --host=educa-legal-development-db-postgresql-do-user-106912-0.a.db.ondigitalocean.com \
  --port=25060 \
  --dbname=educa-legal-test \
  --username=doadmin \
  --no-password \
  --verbose \
  --clean > ${FILENAME}
PGPASSWORD=educalegal dropdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal createdb -U educalegal -h localhost -p 7654 --echo educalegal
PGPASSWORD=educalegal psql -U educalegal -d educalegal -h localhost -e -p 7654 < ${FILENAME}
rm ${FILENAME}