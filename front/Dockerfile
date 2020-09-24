FROM node:12.18.3-buster
RUN mkdir -p /code
COPY . /code
WORKDIR /code
# Apaga pastas e arquivos instalados no ambiente de DEV
RUN ./docker_clean_project.sh
# https://vsupalov.com/docker-build-pass-environment-variables/
# https://stackoverflow.com/questions/58940834/deploying-nuxt-with-docker-env-variables-not-registering-and-unexpect-api-call
ARG BUILD_BACKEND_URL
ENV BACKEND_URL $BUILD_BACKEND_URL
RUN yarn install && yarn build
EXPOSE 3000
