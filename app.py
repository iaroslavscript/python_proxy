#!/usr/bin/env python
# coding: utf-8

import argparse
import http.server
import time
import threading

import requests


class RateLimiter:
    def __init__(self, secs):
        self.__secs = float(secs)
        self.__mutex = threading.Lock()
        self.__last_request = None

    def limit(self):
        self.__mutex.acquire()
        curr_request = time.time()
        if self.__last_request is not None:
            secs = curr_request - self.__last_request

            if secs < self.__secs:
                time.sleep(self.__secs - secs)

        self.__last_request = curr_request
        self.__mutex.release()



class ReverseProxyRequestHandler(http.server.BaseHTTPRequestHandler):
    """known issue:
        - HEADERS with the same name will be taken only once
        - extra "Server" and "Date" headers in response """

    PROXY_URL = ""
    PROXY_HOST = ""
    RATE = None

    def do_HEAD(self):
        self.proxy("HEAD")

    def do_GET(self):
        self.proxy("GET")

    def do_OPTIONS(self):
        self.proxy("OPTIONS")
    
    def do_POST(self):
        self.proxy("POST")
    
    def do_PUT(self):
        self.proxy("PUT")
    
    def do_PATCH(self):
        self.proxy("PATCH")
    
    def do_DELETE(self):
        self.proxy("DELETE")

    def headers_fill(self, headers):

        for k,v in self.headers.items():
            headers[k] = v

    def headers_set_proxy_host(self, headers):

        for k in dict(headers).keys():
            if k.lower() == "host":
                del headers[k]

        headers['Host'] = self.PROXY_HOST

    def proxy(self, method):

        self.RATE.limit()
        
        hh=dict()
        self.headers_fill(hh)
        self.headers_set_proxy_host(hh)

        r = requests.request(
            method,
            headers=hh,
            url=self.PROXY_URL + self.path,
        )
        self.send_response(r.status_code)

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
    ReverseProxyRequestHandler.RATE = RateLimiter(1.0)

    serv = http.server.ThreadingHTTPServer(
        (conf.bind_host, int(conf.bind_port)),
        ReverseProxyRequestHandler)

    serv.serve_forever()


if __name__ == '__main__':
    main()

