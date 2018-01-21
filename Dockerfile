FROM python:3

RUN apt-get update && \
    apt-get install -y ntp && \
    ntpd -gq && \
    service ntp start

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./query.py" ]