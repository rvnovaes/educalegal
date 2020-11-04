#!/bin/bash
make stop
docker system prune -f
docker rmi -f environments_nginx:latest
#docker volume prune -f
docker builder prune -a -f
make run e=test