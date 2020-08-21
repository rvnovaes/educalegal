FROM node:12.18.3-buster as build-stage
RUN mkdir -p /code
WORKDIR /code
COPY . .
# Apaga pastas e arquivos instalados no ambiente de DEV
RUN ./docker_clean_project.sh
# https://stackoverflow.com/questions/58940834/deploying-nuxt-with-docker-env-variables-not-registering-and-unexpect-api-call
ARG BACKEND_URL
ENV BACKEND_URL ${BACKEND_URL}
RUN yarn install && yarn build
EXPOSE 3000
CMD ["yarn", "start", ""]
