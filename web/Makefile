# https://docs.docker.com/compose/extends/
build:
	docker-compose build web

collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

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

load_fixtures:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run web python manage.py loaddata tenant school interview_dev
else
	docker-compose run web python manage.py loaddata tenant school interview_dev
endif

ps:
	docker-compose ps

run:
ifeq ($(e), prod)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
else
	docker-compose up -d
endif

restart:
	docker-compose stop
	docker-compose up -d

shell:
	docker-compose run web bash

stop:
	docker-compose stop