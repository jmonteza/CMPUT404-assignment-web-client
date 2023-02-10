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
        """
        https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol\#HTTP/1.1_response_messages
        ParseResult(scheme='https', netloc='en.wikipedia.org', path='/wiki/Hypertext_Transfer_Protocol', params='', query='', fragment='HTTP/1.1_response_messages')

        https://www.google.com/search\?q\=hello\&aqs\=chrome
        ParseResult(scheme='https', netloc='www.google.com', path='/search', params='', query='q=hello&aqs=chrome', fragment='')

        """
        url = urlparse(url)

        # HTTP
        scheme = url.scheme

        hostname = url.hostname

        # Port 80
        port = url.port

        # /path
        path = url.path

        # Query
        query = url.query

        # Params
        params = url.params

        # Check for HTTP or HTTPS
        if scheme != "http" and scheme != "https":
            scheme = "http"
            print("You must use HTTP or HTTPS")

        # Handle query string (URL attached and from args parameters)
        if query:
            # Attached to the URL (ex. search?q=hello)
            query_string = f"?{query}"
        elif args:
            # Coming from the dictionary in args parameter so we URL encode it
            query_string = f"?{urlencode(args)}"
        else:
            # Empty query string
            query_string = ""

        # Default to port 80
        if port is None:
            port = 80

        # Path cannot be empty, if empty, set it to the root path
        if path == "":
            path = '/'

        # Connect to the server
        try:
            self.connect(hostname, port)
        except:
            print("Connect failed")

        # Send the data
        data = f"""GET {path}{query_string} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36\r\nConnection: close\r\n\r\n"""

        # Send the entire buffer
        try:
            self.sendall(data)
        except:
            print("Send failed")

        # Receive the entire buffer
        try:
            response = self.recvall(self.socket)
        except:
            print("Receive failed")

        # Split between header and body
        splits = response.split("\r\n\r\n")

        # Get the headers
        headers = self.get_headers(splits)

        # Get status code
        code = self.get_code(headers)

        # Get the body
        body = self.get_body(splits)

        # Close the socket
        try:
            self.close()
        except:
            print("Close socket failed")

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # code = 500
        # body = ""

        url = urlparse(url)

        # HTTP
        scheme = url.scheme

        hostname = url.hostname

        # Port 80
        port = url.port

        # /path
        path = url.path

        # Check for HTTP or HTTPS
        if scheme != "http" and scheme != "https":
            scheme = "http"
            print("You must use HTTP or HTTPS")

        # Default to port 80
        if port is None:
            port = 80

        # Path cannot be empty
        if path == "":
            path = '/'

        # Connect to the server
        try:
            self.connect(hostname, port)
        except:
            print("Connect failed")

        # POST has body
        if args:
            request_body = urlencode(args)
            content_length = len(request_body)
        else:
            request_body = ''
            content_length = 0

        # Send the data
        data = f"""POST {path} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{request_body}"""

        # Send the entire buffer
        try:
            self.sendall(data)
        except:
            print("Send failed")

        # Receive the entire buffer
        try:
            response = self.recvall(self.socket)
        except:
            print("Receive failed")

        # Split between header and body
        splits = response.split("\r\n\r\n")

        # Get the headers
        headers = self.get_headers(splits)
        
        # Get status code
        code = self.get_code(headers)

        # Get the body
        body = self.get_body(splits)

        # Close the socket
        try:
            self.close()
        except:
            print("Close socket failed")

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
