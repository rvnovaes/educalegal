#!/bin/bash
export PGPASSFILE="/opt/educalegal/web/pgpass_do"
chmod 600 /opt/educalegal/web/pgpass_do
DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`
FILENAME=educa-legal-app-${DATE_WITH_TIME}.sql
pg_dump --host=educa-legal-producao-db-postgresql-do-user-106912-0.db.ondigitalocean.com \
  --port=25060 \
  --dbname=educa-legal-app \
  --username=educa-legal-app \
  --no-password \
  --verbose \
  --clean > ${FILENAME}
PGPASSWORD=e60k17byidfg20ye dropdb -U educa-legal-app -h educa-legal-producao-db-postgresql-do-user-106912-0.db.ondigitalocean.com -p 25060 --echo educa-legal-test
PGPASSWORD=e60k17byidfg20ye createdb -U educa-legal-app -h educa-legal-producao-db-postgresql-do-user-106912-0.db.ondigitalocean.com -p 25060 --echo educa-legal-test
PGPASSWORD=e60k17byidfg20ye psql -U educa-legal-app -d educa-legal-test -h educa-legal-producao-db-postgresql-do-user-106912-0.db.ondigitalocean.com -e -p 25060 < ${FILENAME}
rm ${FILENAME}