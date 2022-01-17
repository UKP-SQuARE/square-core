## SQuARE Documentation 

### Libraries used

1. Sphinx
2. [Material UI theme](https://bashtage.github.io/sphinx-material/)

### Requirements

1. sphinx==4.3.2
2. sphinx-copybutton==0.4.0	
3. sphinx-markdown-tables==0.0.15	
4. sphinx-material==0.0.35	
5. myst-parser==0.16.1

### Folder Structure

```
├───_build              # contains all build files
├───_static             # custom css files
├───_templates          # custom templates to change website layout
├───images              # add images to use here 
├───pages               # website pages
│   ├───api             # api documentation files
│       ├───datastore_api
│       ├───explainability_api
│       ├───model_api
│       ├───skill_api
│   ├───components      # Docs for different square components
│       ├───datastores.md
│       ├───explainability.md
│       ├───models.md
│       ├───skills.md
│   └───overview        # project overview docs
│       ├───faq.md
│       ├───get_started.md
│       ├───overview.md
│       ├───roadmap.md
│       ├───tutorials.md
│       ├───use_cases.md
├───conf.py              # main configuration for the website
├───index.rst            # main page
├───make.bat             # makefile for windows
├───Makefile             # Makefile to run the project
├───README.md            # documentation
```


### Run

```python
# point to the docs folder
cd docs/
# clean any previous builds
make clean
# create a fresh build
make html
```

