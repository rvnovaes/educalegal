#!/bin/bash
make stop
docker builder prune -a -f
docker rmi -f environments_nginx:latest
docker volume rm -f environments_certbot-var environments_certbot-etc environments_web-root
docker system prune -f