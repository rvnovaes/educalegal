#!/bin/bash
# Adiciona a instrucao para rodar a renovacao do certificado todos os dias pares a meia noite
crontab -l | { cat; echo "0 0 2-30/2 * * /opt/educalegal/environments/dockerfiles/nginx_test/ssl_renew.sh"; } | crontab -