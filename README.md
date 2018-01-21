# Binance Profit Monitor
## Configuration
```bash
$ cp sample-config.yaml config.yaml
```

Edit binance `api_key` and `api_secret` and other details in `config.yaml`

## Build 
```bash
$ docker build -t vijay/binance .
```

## Run as a daemon
```bash
$ docker run -d --rm --name binance -p 8080:8080 --privileged vijay/binance
```

## Run in foreground
```bash
$ docker run -t --rm --name binance -p 8080:8080 --privileged vijay/binance
```

## Curl
```bash
$ curl -D - http://127.0.0.1:8080
```

## Stop container

```bash
$ docker stop binance
```

# License


