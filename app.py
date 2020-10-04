#!/usr/bin/env python
# coding: utf-8

import http.server
import sys

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
        hh["Host"] = self.PROXY_HOST

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




def main():
    
    bind_host = sys.argv[1]
    bind_port  = sys.argv[2]
    proto = sys.argv[3]
    host = sys.argv[4]
    port = sys.argv[5]

    ReverseProxyRequestHandler.PROXY_URL = "{}://{}:{}".format(proto, host, port)
    ReverseProxyRequestHandler.PROXY_HOST = host

    serv = http.server.ThreadingHTTPServer(
        (bind_host, int(bind_port)),
        ReverseProxyRequestHandler)

    serv.serve_forever()


if __name__ == '__main__':
    main()

