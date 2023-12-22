# based on https://vuejs.org/v2/cookbook/dockerize-vuejs-app.html
# Used when running without the compose file

# build stage
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install -g npm@8.1.4
RUN npm ci
COPY . .
ARG mode
RUN npm run build -- --mode $mode

# production stage
FROM nginx:1.23.1-alpine as build
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
