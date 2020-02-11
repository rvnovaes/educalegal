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
	docker-compose run web python manage.py migrate --noinput

makemigrations:
	docker-compose run web python manage.py makemigrations --noinput

load_fixtures:
	docker-compose run web python manage.py loaddata tenant school interview_dev

ps:
	docker-compose ps

run:
	docker-compose up -d

restart:
	docker-compose stop
	docker-compose up -d

shell:
	docker-compose run web bash

stop_web:
	docker-compose stop web nginx

stop:
	docker-compose stop