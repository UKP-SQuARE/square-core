FROM python:3.9.14-slim-buster as base
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
WORKDIR /app

COPY main.py /app/
COPY requirements.txt /app/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
RUN pip install -r requirements.txt

EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["/app/entrypoint.sh"]