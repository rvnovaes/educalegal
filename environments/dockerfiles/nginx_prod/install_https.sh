#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --non-interactive -d app.educalegal.com.br -d api.educalegal.com.br -d generation.educalegal.com.br -d production.educalegal.com.br -d apiflower.educalegal.com.br -d apimongoexpress.educalegal.com.br -d apirabbitmq.educalegal.com.br
docker cp conf_final/api.conf nginx:/etc/nginx/conf.d
docker cp conf_final/docassemble.conf nginx:/etc/nginx/conf.d
docker cp conf_final/educalegal.conf nginx:/etc/nginx/conf.d
docker cp conf_final/menu.conf nginx:/etc/nginx/conf.d
docker cp conf_final/apirabbitmq.conf nginx:/etc/nginx/conf.d
docker cp conf_final/apimongoexpress.conf nginx:/etc/nginx/conf.d
docker cp conf_final/apiflower.conf nginx:/etc/nginx/conf.d
docker cp menu.html nginx:/usr/share/nginx/html
docker restart nginx
crontab -l | { cat; echo "0 0 2-30/2 * * /opt/educalegal/environments/dockerfiles/nginx_test/ssl_renew.sh"; } | crontab -
service cron restart