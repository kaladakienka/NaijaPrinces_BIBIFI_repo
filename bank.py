#!/usr/bin/env python

import argparse
import json
from netmsg import NetMsg
from OptionChecker import OptionChecker
import os
import SocketServer
import sys

auth_key = ""


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.exit(255)


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
        sys.stdout.flush()

    def __str__(self):
        json_out = {}
        json_out["account_name"] = self.account_name
        json_out["balance"] = self.balance
        json_out["card_key"] = self.card_key
        return json.dumps(json_out)

    def print_json(self, json_out):
        print json.dumps(json_out)
        sys.stdout.flush()

    def deposit(self, amount):
        self.balance = self.balance + amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["deposit"] = amount
        self.print_json(json_out)

    def withdraw(self, amount):
        if self.balance < amount:
            return False

        self.balance = self.balance - amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["withdraw"] = amount
        self.print_json(json_out)
        return True

    def get_balance(self):
        return self.balance

    def current_balance(self):
        json_out = {}
        json_out["account"] = self.account_name
        json_out["balance"] = self.balance
        self.print_json(json_out)


class Bank(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    accounts = []

    def send_ack(self, ack):
        ack = NetMsg.encryptedJson(auth_key, ack)
        self.request.sendall(ack)

    def print_to_stderr(self, msg):
        if len(msg) > 0:
            sys.stderr.write(msg)

    def get_acct_w_acct_name_n_card_key(self, account_name, card_key):
        for account in self.accounts:
            if account_name == account.account_name \
               and card_key == account.card_key:
                return account

        return None

    def get_account_w_accout_name(self, account_name):
        for account in self.accounts:
            if account_name == account.account_name:
                return account

        return None

    def get_account_w_card_key(self, card_key):
        for account in self.accounts:
            if card_key == account.card_key:
                return account

        return None

    def parse_request(self, data):
        try:
            # decrypt message
            net_msg = json.loads(NetMsg.decryptJson(auth_key, data))
            msg = net_msg["msg"]
            response = {}
            response["msgID"] = net_msg["msgID"] + 1
            response["code"] = 0

            # perform atm request
            request = msg["request"]
            if request["action"] == "new":
                if request["amount"] < 10:
                    self.print_to_stderr("Amount was less than 10\n")
                    response["msg"] = "transaction_failed"
                    self.send_ack(json.dumps(response))
                    # self.send_ack("transaction_failed")
                    return

                if self.get_acct_w_acct_name_n_card_key(request["accountName"],
                                                        request["pin"]):
                    self.print_to_stderr("Account already exists\n")
                    response["msg"] = "transaction_failed"
                    # self.send_ack("transaction_failed")
                    return

                new_account = Account(request["pin"],
                                      request["accountName"], request["amount"])
                self.accounts.append(new_account)
                response["msg"] = "transaction_completed"
                self.send_ack(json.dumps(response))
                # self.send_ack("transaction_completed")
            elif request["action"] == "deposit":
                if request["amount"] <= 0:
                    self.print_to_stderr("Amount was less than or equal to 0\n")
                    response["msg"] = "transaction_failed"
                    self.send_ack(json.dumps(response))
                    # self.send_ack("transaction_failed")
                    return

                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])

                if account is None:
                    self.print_to_stderr("Could not verify user account\n")
                    response["msg"] = "transaction_failed"
                    self.send_ack(json.dumps(response))
                    # self.send_ack("transaction_failed")
                    return
                else:
                    account.deposit(request["amount"])
                    response["msg"] = "transaction_completed"
                    response["balance"] = account.get_balance()
                    self.send_ack(json.dumps(response))
                    # self.send_ack("transaction_completed")
            elif request["action"] == "withdraw":
                # account = self.get_acct_w_acct_name_n_card_key(request["pin"])
                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])
                if account is None:
                    self.print_to_stderr("Could not verify user account\n")
                    response["msg"] = "transaction_failed"
                    self.send_ack(json.dumps(response))
                    # self.send_ack("transaction_failed")
                    return
                else:
                    if not account.withdraw(request["amount"]):
                        response["msg"] = "transaction_failed"
                        response["code"] = 419
                        self.send_ack(json.dumps(response))
                        # self.request.sendall("419")
                    else:
                        # self.send_ack("transaction_completed")
                        response["msg"] = "transaction_completed"
                        response["balance"] = account.get_balance()
                        self.send_ack(json.dumps(response))
            elif request["action"] == "get":
                account = self.get_acct_w_acct_name_n_card_key(request[
                                                               "accountName"],
                                                               request["pin"])

                if account is None:
                    self.print_to_stderr("Could not verify user account\n")
                    return
                else:
                    account.current_balance()
                    response["msg"] = "transaction_completed"
                    response["balance"] = account.get_balance()
                    self.send_ack(json.dumps(response))
                    # self.send_ack(str(account.get_balance()))
        except ValueError:
            # self.request.sendall("protocol_error")
            response["msg"] = "protocol_error"
            self.send_ack(json.dumps(response))
            print "protocol_error"

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # print "{} wrote:".format(self.client_address[0])
        self.parse_request(self.data)


def exit(msg):
    if len(msg) > 0:
        sys.stderr.write(msg)

    sys.exit(255)


def parse_cmd_line():
    try:
        parser = MyParser()
        parser.add_argument('-p', '--port', help='Port Number',
                            default=3000)
        parser.add_argument('-s', '--auth_file', help='Authenication file name',
                            default="bank.auth")

        args = vars(parser.parse_args())

        # if OptionChecker.checkPortNumber(int(args['port'])):
        #     exit("Port number either too small or too large\n")
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
        # print "created"
    else:
        exit("Authenication file already exists\n")


#TODO: We might want to send acks regardless
def main():
    args = parse_cmd_line()
    if OptionChecker.checkFileName(args["auth_file"]):
        generate_auth_file(args["auth_file"])
    else:
        exit("Invalid file name")

    # Create the server, binding to localhost on port 9999
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(("127.0.0.1", int(args['port'])), Bank)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit


if __name__ == '__main__':
    main()
