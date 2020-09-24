FROM nginx
# Na imagem do Docker nao existe sites-enabled ou sites-available. Fica dentro de conf.d
COPY nginx_prod.conf /etc/nginx/conf.d
COPY nginx_api_prod.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx
RUN mkdir -p /var/log/el_api_prod
RUN mkdir -p /var/log/el_prod
RUN apt-get update && apt-get install -y python-certbot-nginx