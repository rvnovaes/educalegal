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
PGPASSWORD=wxk5gsxfqj8jnru2 dropdb -U doadmin -h educa-legal-development-db-postgresql-do-user-8910843-0.b.db.ondigitalocean.com -p 25060 --echo educa-legal-test
PGPASSWORD=wxk5gsxfqj8jnru2 createdb -U doadmin -h educa-legal-development-db-postgresql-do-user-8910843-0.b.db.ondigitalocean.com -p 25060 --echo educa-legal-test
PGPASSWORD=wxk5gsxfqj8jnru2 psql -U doadmin -d educa-legal-test -h educa-legal-development-db-postgresql-do-user-8910843-0.b.db.ondigitalocean.com -e -p 25060 < /opt/educalegal/scripts/educa-legal-app-20210321-113000.sql
rm ${FILENAME}