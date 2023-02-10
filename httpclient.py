#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
# import urllib.parse
from urllib.parse import urlparse, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data[0].split()[1])

    def get_headers(self, data):
        return data[0].split("\r\n")

    def get_body(self, data):
        return data[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 200
        body = ""
        url = urlparse(url)
        hostname = url.hostname
        port = url.port
        path = url.path
        query = url.query

        print(url)

        if query:
            query_parameters = f"?{query}"
        else:
            query_parameters = ""

        if port is None:
            port = 80

        if path == "":
            # print("stringgg")
            path = '/'

        # print(hostname, port, path)

        # Connect to the server
        self.connect(hostname, port)

        # Send the data
        data = f"""GET {path}{query_parameters} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"""
        print(data)
        self.sendall(data)

        response = self.recvall(self.socket)

        # Split between header and body
        splits = response.split("\r\n\r\n")

        # for split in splits:
        #     print(split)
        #     print("***********")

        # headers = splits[0].split("\r\n")

        headers = self.get_headers(splits)

  

        # code = int(headers[0].split()[1])
        code = self.get_code(headers)

        # body = splits[1]

        body = self.get_body(splits)

        # print(headers)

        # print("*********")

        # print(code)

        # print("*********")

        print(body)

        # self.close()
        # print(response)
        # print(response.decode())
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        url = urlparse(url)
        hostname = url.hostname
        port = url.port
        path = url.path

        print(url, hostname, port, path)

        # Connect to the server
        self.connect(hostname, port)

        content_length = 0
        request_body = ''

        if args:
            request_body = urlencode(args)
            content_length = len(request_body)

        # Send the data
        data = f"""POST {path} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{request_body}"""

        self.sendall(data)

        response = self.recvall(self.socket)

        print(response)

        # Split between header and body
        splits = response.split("\r\n\r\n")

        headers = self.get_headers(splits)

        code = self.get_code(headers)

        body = self.get_body(splits)

        # print(splits)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
