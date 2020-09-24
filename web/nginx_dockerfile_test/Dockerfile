FROM nginx
COPY nginx_test /etc/nginx/sites-available
COPY nginx_api_test /etc/nginx/sites-available
RUN mkdir -p /var/log/el_api_test
RUN mkdir -p /var/log/el_test
RUN apt-get update && apt-get install -y python-certbot-nginx