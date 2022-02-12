FROM python:3.8

ENV PYTHONUNBUFFERED 1

EXPOSE 8501

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

RUN mkdir data

RUN useradd appuser && chown -R appuser data