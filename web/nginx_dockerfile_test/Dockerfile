FROM nginx
# Na imagem do Docker nao existe sites-enabled ou sites-available. Fica dentro de conf.d
COPY nginx_test.conf /etc/nginx/conf.d
COPY nginx_api_test.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx
RUN mkdir -p /var/log/el_api_test
RUN mkdir -p /var/log/el_test
RUN apt-get update && apt-get install -y python-certbot-nginx