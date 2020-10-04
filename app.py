#!/usr/bin/env python
# coding: utf-8

import argparse
import http.server
import random # TODO REMOVE it
import time # TODO REMOVE it
import sys
import threading

import requests


class RateLimiter:
    def __init__(self, secs):
        self.__secs = float(secs)
        self.__mutex = threading.Lock()
        self.__last_request = None

    def limit(self, r_id):
        self.__mutex.acquire()
        print("{}\t{}\t{}".format(time.ctime(), r_id, "acquire"))
        curr_request = time.time()
        if self.__last_request is not None:
            secs = curr_request - self.__last_request

            if secs < self.__secs:
                print("{}\t{}\t{}".format(time.ctime(), r_id, "secs="+str(secs)))
                time.sleep(self.__secs - secs)

        self.__last_request = curr_request
        print("{}\t{}\t{}".format(time.ctime(), r_id, "release"))
        self.__mutex.release()



class ReverseProxyRequestHandler(http.server.BaseHTTPRequestHandler):

    PROXY_URL = ""
    PROXY_HOST = ""
    RATE = None

    def do_HEAD(self):
        self.proxy("HEAD")

    def do_GET(self):
        self.proxy("GET")

    def headers_fill(self, headers):

        for k,v in self.headers.items():
            headers[k] = v

    def headers_set_proxy_host(self, headers):

        for k in dict(headers).keys():
            if k.lower() == "host":
                del headers[k]

        headers['Host'] = self.PROXY_HOST

    def proxy(self, method):

        r_id = random.randint(1000000, 10000000)

        print("{}\t{}\t{}".format(time.ctime(), r_id, "HELLO"))
        self.RATE.limit(r_id)

        print("{}\t{}\t{}".format(time.ctime(), r_id, "REQUEST"))

        x = random.randint(3, 15)
        print("{}\t{}\t{}".format(time.ctime(), r_id, "Sleep for " + str(x)))
        time.sleep(x)

        # TODO timeout
        # known issue HEADERS with the same name will be taken only once
        
        hh=dict()
        self.headers_fill(hh)
        self.headers_set_proxy_host(hh)

        r = requests.request(
            method,
            headers=hh,
            url=self.PROXY_URL + self.path,
        )
        self.send_response(r.status_code)

        #if "Server" in self.headers:
        #    del self.headers["Server"]
        #
        #if "Date" in self.headers:
        #   del self.headers["Date"]

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

