#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --non-interactive -d apptest.educalegal.com.br -d apitest.educalegal.com.br -d doctest.educalegal.com.br -d test.educalegal.com.br -d apiflowertest.educalegal.com.br -d apimongoexpresstest.educalegal.com.br -d apirabbitmqtest.educalegal.com.br
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