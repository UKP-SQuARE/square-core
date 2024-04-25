FROM node:lts-alpine as docs-build-stage

LABEL maintainer="Rachneet Sachdeva <sachdeva@ukp.informatik.tu-darmstadt.de>" \
      description="Docker container for the square documentation website"

WORKDIR /square-docs
COPY package*.json ./

RUN npm install -g npm@8.5.2
RUN npm ci

COPY . .
RUN npm run build

# production stage
FROM nginx:1.26-alpine as build
COPY --from=docs-build-stage /square-docs/build /www/data/docs
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
