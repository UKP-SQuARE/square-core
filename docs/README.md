# SQuARE Documentation Website

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

# Project structure

```
├───build                      # contains all build files after build
├───static                     # image files
├───home                       # main docs
│   ├───components             # models, datastores, and skills docs
│   ├───overview               # overview docs
│   └───changelog.md           # docs versions
├───src               
│   ├───components             # Home page elements
│   ├───css                    # website styling
│   └───pages                  # index page
├───docusaurus.config.js       # website config
├───nginx.conf                 # webserver config
├───pakage.json                # scripts and packages
├───dockerfile                 # docker build 
├───docker-compose.yml         # build config
├───sidebars.js                # sidebars config
└───requirements.txt           # libraries needed
```

### How to use?

#### Adding static content

1. <u>Images:</u> add all the images in the ``static/img`` folder.

#### Installation

```
$ yarn or npm
```

#### Local Development

```
$ yarn start or npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

#### Build

```
$ yarn build or npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.
