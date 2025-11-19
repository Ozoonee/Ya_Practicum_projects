FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install setuptools
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn==23.0.0 

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "kittygram_backend.wsgi"]
