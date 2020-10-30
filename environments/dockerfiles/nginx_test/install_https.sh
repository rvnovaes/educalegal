#!/bin/bash
docker exec nginx certbot certonly --nginx --email sistemas@educalegal.com.br --agree-tos --staging --non-interactive -d apptest.educalegal.com.br -d apitest.educalegal.com.br
docker cp conf_final/api.conf nginx:/etc/nginx/conf.d
docker cp conf_final/educalegal.conf nginx:/etc/nginx/conf.d