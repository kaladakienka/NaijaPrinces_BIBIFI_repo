#!/usr/bin/env/python

import argparse
import json
from netmsg import NetMsg
import os
import sys
import SocketServer

auth_key = ""


class Account:
    card_key = ""
    account_name = ""
    balance = 0

    #TODO:Both programs should explicitly flush stdout after every line printed.
    def __init__(self, card_key, name, balance):
        self.card_key = card_key
        self.account_name = name
        self.balance = balance
        json_out = {}
        json_out["account"] = self.account_name
        json_out["initial_balance"] = self.balance
        print json.dumps(json_out)

    def __str__(self):
        json_out = {}
        json_out["account_name"] = self.account_name
        json_out["balance"] = self.balance
        json_out["card_key"] = self.card_key
        return json.dumps(json_out)

    def deposit(self, amount):
        self.balance = self.balance + amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["deposit"] = amount
        print json.dumps(json_out)

    def withdraw(self, amount):
        if self.balance < amount:
            return False

        self.balance = self.balance - amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["withdraw"] = amount
        print json.dumps(json_out)

    def current_balance(self):
        json_out = {}
        json_out["account"] = self.account_name
        json_out["balance"] = self.balance
        print json.dumps(json_out)


class Bank(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    accounts = []

    def get_acct_w_acct_name_n_card_key(self, account_name, card_key):
        for account in self.accounts:
            if account_name == account.account_name \
               and card_key == account.card_key:
                return account

    def get_account_w_accout_name(self, account_name):
        for account in self.accounts:
            if account_name == account.account_name:
                return account

    def get_account_w_card_key(self, card_key):
        for account in self.accounts:
            if card_key == account.card_key:
                return account

    def parse_request(self, data):
        try:
            # decrypt message
            net_msg = json.loads(NetMsg.decryptJson(auth_key, data))
            msg = net_msg["msg"]

            # perform atm request
            request = msg["request"]
            if request["action"] == "new":
                if request["amount"] < 10:
                    sys.stderr.write(255)
                    sys.exit(255)

                if self.get_acct_w_acct_name_n_card_key(request["pin"],
                                                        request["pin"]):
                    sys.stderr.write(255)
                    sys.exit(255)

                new_account = Account(request["pin"],
                                      request["accountName"], request["amount"])
                self.accounts.append(new_account)
            elif request["action"] == "deposit":
                if request["amount"] <= 0:
                    sys.stderr.write(255)
                    sys.exit(255)

                if self.get_acct_w_acct_name_n_card_key(request["pin"],
                                                        request["pin"]):
                    sys.stderr.write(255)
                    sys.exit(255)

                # account = self.get_acct_w_acct_name_n_card_key(request["pin"])
                # print "Depositing money"
                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])
                account.deposit(request["amount"])
            elif request["action"] == "withdraw":
                # account = self.get_acct_w_acct_name_n_card_key(request["pin"])
                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])

                #TODO: Find out if John is handling this
                if not account.withdraw(request["amount"]):
                    self.request.sendall("419")
            elif request["action"] == "get":
                # account = self.get_acct_w_acct_name_n_card_key(request["pin"])
                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])
                account.current_balance()
        except ValueError:
            print "protocol_error"

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # print "{} wrote:".format(self.client_address[0])
        # print self.data
        self.parse_request(self.data)

        # just send back the same data, but upper-cased
        # self.request.sendall(self.data.upper())


def exit(msg):
    if len(msg) > 0:
        sys.stderr.write(msg)

    sys.exit(255)


def parse_cmd_line():
    parser = argparse.ArgumentParser(description='bank is a server that \
                                    simulates a bank, whose job is to keep \
                                    track of the balance of its customers. ')
    parser.add_argument('-p', '--port', help='Description for foo argument',
                        required=True, default=3000)
    parser.add_argument('-s', '--auth_file', help='Description for bar \
                        argument', required=True)

    try:
        args = vars(parser.parse_args())

        if int(args['port']) < 1024 or int(args['port']) > 65535:
            exit("Port number either too small or too large\n")
    except SystemExit:
        exit("Invalid command line options provided\n")

    return args


def generate_auth_file(auth_file):
    global auth_key
    if not os.path.isfile(auth_file):
        f = open(auth_file, "wb")
        json_out = {}
        json_out["SecretKey"] = NetMsg.generateKey()
        auth_key = json_out["SecretKey"]
        f.write(json.dumps(json_out))
        f.close()
        print "created"
    else:
        sys.exit(255)


#TODO: We might want to send acks regardless
def main():
    args = parse_cmd_line()

    # Create the server, binding to localhost on port 9999
    generate_auth_file(args["auth_file"])
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(("127.0.0.1", int(args['port'])), Bank)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


if __name__ == '__main__':
    main()
