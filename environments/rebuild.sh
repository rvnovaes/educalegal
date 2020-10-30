#!/bin/bash
make stop
docker system prune -f
docker rmi -f environments_nginx:latest
docker volume rm -f environments_certbot-var environments_certbot-etc environments_web-root
docker builder prune -a -f