#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --non-interactive -d apptest.educalegal.com.br -d apitest.educalegal.com.br
docker cp conf_final/api.conf nginx:/etc/nginx/conf.d
docker cp conf_final/educalegal.conf nginx:/etc/nginx/conf.d
docker restart nginx
source ./add_renew_crontab.sh
service crontab restart