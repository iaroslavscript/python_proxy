#!/usr/bin/env python
# coding: utf-8

import argparse
import http.server

import requests


class ReverseProxyRequestHandler(http.server.BaseHTTPRequestHandler):

    PROXY_URL = ""
    PROXY_HOST = ""

    def do_HEAD(self):
        self.proxy("HEAD")

    def do_GET(self):
        self.proxy("GET")


    def proxy(self, method):

        hh = {k:v for k,v in self.headers.items()}
        for k, v in dict(hh).items():
            if k.lower() == "host":
                del hh[k]

        hh['Host'] = self.PROXY_HOST

        r = requests.request(
            method,
            headers=hh,
            url=self.PROXY_URL + self.path,
        )
        self.send_response(r.status_code)

        if "Server" in self.headers:
            del self.headers["Server"]

        if "Date" in self.headers:
            del self.headers["Date"]

        for k,v in r.headers.items():
            self.send_header(k, v)

        
        self.end_headers()
        self.wfile.write(r.content)


def parse_args():

    parser = argparse.ArgumentParser(description='Simple python reverse proxy')

    parser.add_argument(
        'proto',
        default='http',
        help='proxy protocol')
    parser.add_argument(
        'host',
        help='proxy server host')
    parser.add_argument(
        'port',
        type=int,
        help='proxy server port')
    parser.add_argument(
        '--bind-host',
        default="localhost",
        help='server bind port')
    parser.add_argument(
        '--bind-port',
        default=8080,
        type=int,
        help='server bind port')

    return parser.parse_args()

def main():

    conf = parse_args()

    ReverseProxyRequestHandler.PROXY_URL = "{}://{}:{}".format(
        conf.proto,
        conf.host,
        conf.port)

    ReverseProxyRequestHandler.PROXY_HOST = conf.host

    serv = http.server.ThreadingHTTPServer(
        (conf.bind_host, int(conf.bind_port)),
        ReverseProxyRequestHandler)

    serv.serve_forever()


if __name__ == '__main__':
    main()

