cd "web/docker-compose.override.yml"
docker-compose stop
certbot renew --force-renewal
docker-compose up -d