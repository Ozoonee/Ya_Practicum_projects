FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install setuptools
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn==23.0.0 

COPY . .

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 backend.wsgi"]
