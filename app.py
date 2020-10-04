#!/usr/bin/env python
# coding: utf-8

import http.server


class ReverseProxyRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        pass



def main(host, port):
    
    serv = http.server.ThreadingHTTPServer(
        (host, port),
        ReverseProxyRequestHandler)

    serv.serve_forever()


if __name__ == '__main__':
    main("localhost", 8080)

