# based on https://vuejs.org/v2/cookbook/dockerize-vuejs-app.html

# build stage
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install -g npm@8.1.4
RUN npm ci
COPY . .
RUN npm run build

# docs stage
FROM python:3.7.6-buster as docs-stage
WORKDIR /app
COPY docs/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY docs/. .
RUN make clean
RUN make html

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY --from=docs-stage /app/_build/html /www/data/docs/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]