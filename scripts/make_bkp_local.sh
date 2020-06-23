#!/bin/sh
pg_dump -hlocalhost -p7654 -deducalegal -Ueducalegal --verbose --clean > "/opt/bkp/el.sql"
