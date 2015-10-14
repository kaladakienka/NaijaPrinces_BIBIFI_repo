#!/usr/bin/env python
import os, sys, re
import optparse
import socket
import json
import uuid
from netmsg import NetMsg

parser = optparse.OptionParser()

cmdlineOptions = optparse.OptionGroup(parser, "Command line options", "These are the base configurations for the atm program")
cmdlineOptions.add_option("-a", metavar="<account>", type="string", help="Name of the account")
cmdlineOptions.add_option("-s", metavar="<auth-file>", type="string", default="./bank.auth", help="Authentication file for the account. [default: %default]")
cmdlineOptions.add_option("-i", metavar="<ip-address>", type="string", default="127.0.0.1", help="IP address for the bank. [default: %default]")
cmdlineOptions.add_option("-p", metavar="<port>", type="int", default=3000, help="TCP port that the bank is listening on. [default: %default]")
cmdlineOptions.add_option("-c", metavar="<card-file>", type="string", help="Customer's atm card file. [default: <account-name>.card]")
parser.add_option_group(cmdlineOptions)

modesOfOperation = optparse.OptionGroup(parser, "Modes of operation", "These options determine what a specific run of the atm program will do")
modesOfOperation.add_option("-n", metavar="<balance>", type="int", help="Create a new account with the given balance")
modesOfOperation.add_option("-d", metavar="<amount>", type="int", help="Deposit this amount of money in the account")
modesOfOperation.add_option("-w", metavar="<amount>", type="int", help="Withdraw this amount from the account")
modesOfOperation.add_option("-g", action="store_true", help="Get the current balance of the account")
parser.add_option_group(modesOfOperation)

(options, args) = parser.parse_args() #Read the options and the arguments from the command line

#Sanity checks
#Check that account name and mode of operation are provided
if options.a == None:
    sys.exit(255)
elif not options.n and not options.d and not options.w and not options.g:
    sys.exit(255)
elif options.n and (options.d or options.w or options.g):
    sys.exit(255)
elif options.d and (options.n or options.w or options.g):
    sys.exit(255)
elif options.w and (options.n or options.d or options.g):
    sys.exit(255)
elif options.g and (options.n or options.w or options.d):
    sys.exit(255)

#Check that file names meets specifications
if len(options.s) > 255 or len(options.s) < 1:
    sys.exit(255)
    
if len(options.a) > 250 or len(options.a) < 1:
    sys.exit(255)

#Create card file index
if not os.path.exists("./CardFiles/"):
    os.makedirs("./CardFiles/")

indexFile = open("./CardFiles/index", "a+")
if len(indexFile.read()) == 0: #New file
    indexData = {}
else:
    indexFile.seek(0)
    indexData = json.loads(indexFile.read())

#Check that authFile exists.
try:
    authFile = open(options.s)
except IOError, e:
    sys.exit(255)

#Check that cardFile exists
if options.c == None:
    options.c = options.a + ".card"
if len(options.c) > 255 or len(options.c) < 1:
    sys.exit(255)

try:
    if indexData[options.a] == options.c and options.n: #Trying to make a new account when it already exists
        sys.exit(255)
    elif indexData[options.a] != options.c: #The card file you passed does not match the file we expect
        sys.exit(255)
except KeyError:
    for entry in indexData:
        if indexData[entry] == options.c: #If card file is associated with another account
            sys.exit(255)

cardFilePath = os.path.join("./CardFiles", options.c)    
if not os.path.exists(cardFilePath) and options.n:
    cardFile = open(cardFilePath, "a+")
    cardPin = NetMsg.generateKey()
    cardFile.write(cardPin)
    cardFile.close()
    
    accountData = {}
    accountData[options.a] = options.c
    indexFile.write(json.dumps(accountData))
    indexFile.close()

#Check that ipAddress meets specifications
ipAddress = options.i.split(".")
for number in ipAddress:
    try:
        number = int(number, base=10)
        if number < 0 or number > 255:
            sys.exit(255)
    except ValueError:
        sys.exit(255)

#Check that port is within range
if options.p < 1024 or options.p > 65535:
    sys.exit(255)


def getAuthKey():
    key = {}
    numLines = 0
    for line in authFile:
        # print line
        key = json.loads(line)
        numLines += 1
    
    if numLines > 1:
        print "WARNING: More than 1 line in authFile"
    # print key
    return str(key["SecretKey"])

def getCardPin():
    numLines = 0
    for line in open(cardFilePath):
        cardPin = line
        numLines += 1
    
    if numLines > 1:
        print "WARNING: More than 1 line in cardFile"
    return cardPin

def main():
    #Getting here implies all pre-requisites have been met (NOT FINISHED!)
    accountName = options.a
    ipAddress = options.i
    port = options.p

    request = {}
    request["accountName"] = accountName
    request["pin"] = getCardPin()
    if options.n:
        request["action"] = "new"
        request["amount"] = options.n
    elif options.d:
        request["action"] = "deposit"
        request["amount"] = options.d
    elif options.w:
        request["action"] = "withdraw"
        request["amount"] = options.w
    elif options.g:
        request["action"] = "get"

    request = {"request" : request}
    print request
    message = NetMsg(request)
    encodedMessage = message.encryptedJson(getAuthKey(), message.getJson())


    print "Running atm with the following settings"
    print "Account Name is", accountName
    print "Bank's IP is", ipAddress
    print "Bank's port is", port
    print "Authentication file is", options.s
    print "Card file is", options.c
    print "Message is", encodedMessage

    # Create socket and send data to bank
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ipAddress, port))
        sock.sendall(encodedMessage)
        received = sock.recv(1024)
    except socket.error, e:
        print e
    finally:
        sock.close()

    print "Finished"

if __name__ == "__main__":
    main()
        
    
