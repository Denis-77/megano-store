FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /django_store

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY store ./store
COPY megano-frontend ./megano-frontend

RUN pip install ./megano-frontend/dist/megano-frontend-0.6.tar.gz

CMD ["gunicorn", "store.store.wsgi:application", "--bind", "0.0.0.0:8000"]
