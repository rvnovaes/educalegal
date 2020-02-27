build:
	docker-compose build web

# parametros
# e=prod - conecta como producao
# e=nodebug - conecta sem modo de debug (-d: detached mode)
# se nao passar o parametro - conecta com modo de debug
# make run e=prod or make run e=nodebug or make run
run:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else ifeq ($(e), nodebug)
	docker-compose up -d
else
	docker-compose up
endif

stop:
	docker-compose stop

restart: stop run

collectstatic:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py collectstatic --noinput
else
	docker-compose run web python manage.py collectstatic --noinput
endif

migrate:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py migrate --noinput
else
	docker-compose run web python manage.py migrate --noinput
endif

makemigrations:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py makemigrations --noinput
else
	docker-compose run web python manage.py makemigrations --noinput
endif

loaddata_prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py loaddata tenant country state city school interview_document_types interview

# Loads fixtures for development
loaddata_dev:
	docker-compose run web python manage.py loaddata tenant country state city school interview_document_types interview_dev

# Creates Educa Legal superuser as admin / Silex2109
create_super_user_educa_legal:
	docker-compose run web ./create_super_user_educa_legal.sh

# Makes the migrations
# Migrates
# Loads fixtures for development
setup_dev: makemigrations migrate loaddata_dev
	-make create_super_user_educa_legal

# Removes old docassemble image
# Builds new educa legal image
# Restarts everything
# It is still necessary to run make setup_dev
fresh_install:
	# https://stackoverflow.com/questions/2670130/make-how-to-continue-after-a-command-fails
	-docker rmi -f jhpyle/docassemble
	make build
	make restart

logs:
	docker-compose logs --follow

ps:
	docker-compose ps

shell:
	docker-compose run web bash




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
