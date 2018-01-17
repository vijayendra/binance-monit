FROM python:3

WORKDIR /opt/app

COPY requirements.txt .
COPY config.js .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./query.py" ]