FROM python:3.9.14-slim-buster as base
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install --upgrade pip
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

COPY main.py /app/

EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["/app/entrypoint.sh"]