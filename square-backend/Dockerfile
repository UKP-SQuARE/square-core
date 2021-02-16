FROM python:3.7.6

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
# not in requirements because we use SQLite for dev server
RUN pip install psycopg2

COPY ./squareapi /app/squareapi
COPY flask_manage.py /app/flask_manage.py
COPY main.py /app/main.py
COPY ./docker /app
COPY __init__.py /app/__init__.py
COPY ./templates /app/templates

WORKDIR /app
RUN mkdir -p logs

RUN ["chmod", "+x", "./entry.sh"]
ENTRYPOINT ["./entry.sh"]
