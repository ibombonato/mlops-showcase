FROM python:3.8.10-slim

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc make

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "Makefile", "./"]
COPY src/ /app/src/

RUN python -m pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile

ENV PATH=".venv/bin:$PATH"

    #pip install pipenv && \
    #pipenv lock --keep-outdated --requirements > requirements.txt && \
    #pip install -r requirements.txt

#RUN pipenv install --system --deploy --ignore-pipfile

#RUN pip install pipenv
#RUN pipenv requirements > requirements.txt
#RUN pipenv lock --keep-outdated --requirements > requirements.txt
#RUN pip install -r requirements.txt

RUN mkdir output

ENTRYPOINT ["python","src/model_predict.py"]
