# python_proxy
Simple reverse proxy

## Usage example:

```
python3 app.py --bind-host=localhost --bind-port=8080 http httpbin.org 80
```

## Docker example

```
docker build -t python-proxy .
docker run -d --publish 8080:8080 python-proxy
```

## Help
```
usage: app.py [-h] [--timeout TIMEOUT] [--bind-host BIND_HOST]
              [--bind-port BIND_PORT]
              proto host port

Simple python reverse proxy

positional arguments:
  proto                 proxy protocol
  host                  proxy server host
  port                  proxy server port

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     proxy server request timeout in milliseconds (default 60000)
  --bind-host BIND_HOST server bind port (default localhost)
  --bind-port BIND_PORT server bind port (default 8080)
```
