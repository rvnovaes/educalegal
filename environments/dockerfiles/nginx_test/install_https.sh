#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --non-interactive -d apptest.educalegal.com.br -d apitest.educalegal.com.br -d doctest.educalegal.com.br -d test.educalegal.com.br
docker cp conf_final/api.conf nginx:/etc/nginx/conf.d
docker cp conf_final/docassemble.conf nginx:/etc/nginx/conf.d
docker cp conf_final/educalegal.conf nginx:/etc/nginx/conf.d
docker cp conf_final/menu.conf nginx:/etc/nginx/conf.d
docker cp menu.html nginx:/usr/share/nginx/html
docker restart nginx
source ./add_renew_crontab.sh
service cron restart