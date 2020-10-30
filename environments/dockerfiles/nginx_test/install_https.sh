#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --non-interactive -d apptest.educalegal.com.br -d apitest.educalegal.com.br
docker cp conf_final/api.conf nginx:/etc/nginx/conf.d
docker cp conf_final/educalegal.conf nginx:/etc/nginx/conf.d
docker restart nginx
crontab -l | { cat; echo "0 0 2-30/2 * * /opt/educalegal/environments/dockerfiles/nginx_test/ssl_renew.sh"; } | crontab -