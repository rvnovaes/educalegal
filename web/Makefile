build:
	docker-compose build web

collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

create_certificate:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d app.educalegal.com.br -m sistemas@educalegal.com.br --agree-tos

create_certificate_teste:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d app.educalegal.com.br -m sistemas@educalegal.com.br --agree-tos

deploy: check_compose_override build restart migrate collectstatic load_fixtures

dev_mode: restart
	docker-compose stop web ws-worker
	docker-compose run web bash -c "ip addr; python manage.py runserver 0:8005"

local_sqlserver:
	ln -s docker-compose.sqlserver.yml docker-compose.override.yml

logs:
	docker-compose logs --follow

migrate:
	docker-compose run web python manage.py migrate --noinput

makemigrations:
	docker-compose run web python manage.py makemigrations --noinput

load_fixtures0:
	docker-compose run web python manage.py loaddata auth_user office country state court_district
	docker-compose run web python manage.py ezl_create_groups_and_permissions

load_fixtures:
	docker-compose run web python manage.py ezl_create_groups_and_permissions

ps:
	docker-compose ps

run:
	docker-compose up -d

restart:
	docker-compose stop
	docker-compose up -d

set_env_development:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.development.yml docker-compose.override.yml

set_env_production:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.production.yml docker-compose.override.yml

set_env_teste:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.teste.yml docker-compose.override.yml

shell:
	docker-compose run web bash

stop_web:
	docker-compose stop web nginx

stop:
	docker-compose stop