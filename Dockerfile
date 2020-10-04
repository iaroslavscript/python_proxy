FROM python:3.7

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt


WORKDIR /app
EXPOSE 8080
CMD [ "python", "/app/app.py", "--bind-host=0.0.0.0", "--bind-port=8080", "http", "httpbin.org", "80"]
