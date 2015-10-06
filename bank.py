#!/usr/bin/env/python

import argparse
import sys
import SocketServer
import uuid


class Bank(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def generate_auth_file(self):
        uid = uuid.uuid4()
        uid.hex

    def setup(self):
        print self.server.auth_file

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


def parse_cmd_line():
    parser = argparse.ArgumentParser(description='bank is a server than \
                                    simulates a bank, whose job is to keep \
                                    track of the balance of its customers. ')
    parser.add_argument('-p', '--port', help='Description for foo argument',
                        required=True)
    parser.add_argument('-s', '--auth_file', help='Description for bar \
                        argument', required=True)

    try:
        args = vars(parser.parse_args())
    except SystemExit:
        sys.exit()

    return args


def main():
    args = parse_cmd_line()

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer(("localhost", int(args['port'])), Bank)
    server.auth_file = args['auth_file']

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


if __name__ == '__main__':
    main()
