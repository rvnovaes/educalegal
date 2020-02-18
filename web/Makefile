# https://docs.docker.com/compose/extends/
build:
	docker-compose build web

collectstatic:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py collectstatic --noinput
else
	docker-compose run web python manage.py collectstatic --noinput
endif

create_certificate:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d app.educalegal.com.br -m sistemas@educalegal.com.br --agree-tos

create_certificate_test:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d app.educalegal.com.br -m sistemas@educalegal.com.br --agree-tos

logs:
	docker-compose logs --follow

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
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py loaddata tenant school interview

loaddata_dev:
	docker-compose run web python manage.py loaddata tenant school interview_dev

# Not working
install_docassemble_python_packages:
	docker-compose run docassemble /usr/share/docassemble/local3.6/bin/pip install coreapi docassemble-wrappers num2words

ps:
	docker-compose ps

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

restart:
	docker-compose stop
	docker-compose up -d

shell:
	docker-compose run web bash

stop:
	docker-compose stop

setup_dev: install_docassemble_python_packages migrate makemigrations loaddata_dev