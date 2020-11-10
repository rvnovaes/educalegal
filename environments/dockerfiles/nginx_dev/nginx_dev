FROM nginx
# Na imagem do Docker nao existe sites-enabled ou sites-available. Fica dentro de conf.d
COPY menu.html /usr/share/nginx/html
COPY *.conf /etc/nginx/conf.d/
COPY proxy_params /etc/nginx
RUN mkdir -p /var/log/nginx
