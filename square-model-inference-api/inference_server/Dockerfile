FROM python:3.8.2 as build

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./tests/pre_test_setup_for_docker_caching.py ./tests/pre_test_setup_for_docker_caching.py
RUN python ./tests/pre_test_setup_for_docker_caching.py

COPY . ./

FROM base as test
WORKDIR /app
RUN pip install pytest pytest-cov pytest-asyncio
COPY ../tests tests
RUN pytest --cov

FROM base as build

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]