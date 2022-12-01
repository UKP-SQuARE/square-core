## This is the dockerfile template for onnx based model
FROM ukpsquare/model-inference-base-model:latest as build

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ./dockerfiles/onnx/requirements.txt ./requirements.onnx.txt
RUN pip install -r requirements.onnx.txt


## Testing stage. We first pre-download any models separately for caching (pre_test_setup_for_docker_caching.py) and then
## run the tests
#FROM build as test
#
#RUN pip install pytest pytest-cov pytest-asyncio pytest-env
#RUN mkdir test-reports
#
## copy application files
#COPY ./app ./app
#COPY main.py main.py
#COPY logging.conf logging.conf
#COPY ./tasks tasks
#
## copy test files
#COPY tests/pre_test_setup_for_docker_caching.py tests/pre_test_setup_for_docker_caching.py
#COPY tests/$MODEL tests/$MODEL
#COPY tests/generic/ tests/$MODEL/generic
#COPY pytest.ini pytest.ini
#
## run tests
##RUN python ./tests/pre_test_setup_for_docker_caching.py --transformer
#
#RUN PYTHONPATH=./ pytest \
#    --junitxml=test-reports/junit.xml \
#    --cov \
#    --cov-report=xml:test-reports/coverage.xml \
#    --cov-report=html:test-reports/coverage.html; \
#    echo $? > test-reports/pytest.existcode
