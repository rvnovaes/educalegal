buildf:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build educalegal
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml build educalegal
else
	docker-compose build educalegal
endif

buildb:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build api apicelery apiflower
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml build api apicelery apiflower
else
	docker-compose build educalegal
endif

builda:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build educalegal api apicelery apiflower
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml build educalegal api apicelery apiflower
else
	docker-compose build educalegal apicelery api apiflower
endif

run:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else ifeq ($(e), nodebug)
	docker-compose up -d
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
else
	docker-compose up
endif

stop:
	docker-compose stop

restart: stop run

collectstatic:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run api python manage.py collectstatic --noinput
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run api python manage.py collectstatic --noinput
else
	docker-compose run api python manage.py collectstatic --noinput
endif

migrate:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run api python manage.py migrate --noinput
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run api python manage.py migrate --noinput
else
	docker-compose run api python manage.py migrate --noinput
endif

makemigrations:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run api python manage.py makemigrations --noinput
else ifeq ($(e), test)
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run api python manage.py makemigrations --noinput
else
	docker-compose run api python manage.py makemigrations --noinput
endif

# Loads fixtures for development
loaddata_dev:
	docker-compose run educalegal python manage.py loaddata tenant school interview_document_types interview_server_config interview

# Creates Educa Legal superuser as admin / Silex2109
create_super_user:
	docker-compose exec api ./create_super_user.shls

logs:
	docker-compose logs --follow

shellf:
	docker-compose run api bash

shellb:
	docker-compose run api bash

# Use the task da_app_remote_to_local to dump production database into local docker container
db_app_start:
	docker-compose start db

db_app_synchronize:
	./scripts/pg_dump_digital_ocean_to_local_educalegal_app.sh

db_app_stop:
	docker-compose stop db

db_app_remote_to_local: db_app_start db_app_synchronize db_app_stop

make_bkp_local:
	./scripts/make_bkp_local.sh

restore_bkp_local:
	./scripts/restore_bkp_local.sh


# https://docs.docker.com/compose/extends/
#What’s the difference between up, run, and start?
# UP - Typically, you want docker-compose up. Use up to start or restart all the services defined
# in a docker-compose.yml. In the default “attached” mode, you see all the logs from all the
# containers. In “detached” mode (-d), Compose exits after starting the containers, but the containers
# continue to run in the background.
# RUN - The docker-compose run command is for running “one-off” or “adhoc” tasks. It requires the service
# name you want to run and only starts containers for services that the running service depends on.
# Use run to run tests or perform an administrative task such as removing or adding data to a data volume
# container. The run command acts like docker run -ti in that it opens an interactive terminal to the
# container and returns an exit status matching the exit status of the process in the container.
# START - The docker-compose start command is useful only to restart containers that were previously created,
# but were stopped. It never creates new containers.
