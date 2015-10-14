#!/usr/bin/env python
import os, sys, re
import optparse
import socket
import json
import uuid
from netmsg import NetMsg
from OptionChecker import OptionChecker

parser = optparse.OptionParser()

cmdlineOptions = optparse.OptionGroup(parser, "Command line options", "These are the base configurations for the atm program")
cmdlineOptions.add_option("-a", metavar="<account>", type="string", help="Name of the account")
cmdlineOptions.add_option("-s", metavar="<auth-file>", type="string", default="bank.auth", help="Authentication file for the account. [default: %default]")
cmdlineOptions.add_option("-i", metavar="<ip-address>", type="string", default="127.0.0.1", help="IP address for the bank. [default: %default]")
cmdlineOptions.add_option("-p", metavar="<port>", type="string", default=3000, help="TCP port that the bank is listening on. [default: %default]")
cmdlineOptions.add_option("-c", metavar="<card-file>", type="string", help="Customer's atm card file. [default: <account-name>.card]")
parser.add_option_group(cmdlineOptions)

modesOfOperation = optparse.OptionGroup(parser, "Modes of operation", "These options determine what a specific run of the atm program will do")
modesOfOperation.add_option("-n", metavar="<balance>", type="string", help="Create a new account with the given balance")
modesOfOperation.add_option("-d", metavar="<amount>", type="string", help="Deposit this amount of money in the account")
modesOfOperation.add_option("-w", metavar="<amount>", type="string", help="Withdraw this amount from the account")
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
    
#Check that modes of operation values are valid:
if options.n and (not OptionChecker.checkFloat(options.n) or float(options.n) < 10.00):
    sys.exit(255)
if options.d and (not OptionChecker.checkFloat(options.d) or float(options.d)) <= 0.00:
    sys.exit(255)
if options.w and (not OptionChecker.checkFloat(options.w) or float(options.w)) <= 0.00:
    sys.exit(255)

#Check that file and account names meets specifications
if not OptionChecker.checkFileName(os.path.split(options.s)[-1]):
    sys.exit(255)
if not OptionChecker.checkAccountName(options.a):
    sys.exit(255)

#Check that ipAddress meets specifications
if not OptionChecker.checkIPAddress(options.i):
    sys.exit(255)

#Check that port is within range
if not OptionChecker.checkPortNumber(options.p):
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
    indexFile.close()

#Check that authFile exists.
try:
    authFile = open(options.s)
except IOError, e:
    sys.exit(255)

#Check that cardFile exists
if options.c == None:
    options.c = options.a + ".card"
if not OptionChecker.checkFileName(options.c):
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
    cardFile = open(cardFilePath, "w")
    cardPin = NetMsg.generateKey()
    cardFile.write(cardPin)
    cardFile.close()
    
    indexData[options.a] = options.c
    indexFile = open("./CardFiles/index", "w")
    indexFile.write(json.dumps(indexData))
    indexFile.close()


def getAuthKey():
    key = {}
    numLines = 0
    for line in authFile:
        key = json.loads(line)
        numLines += 1
    
    if numLines > 1:
        print >> sys.stderr, "WARNING: More than 1 line in authFile"
        sys.stdout.flush()
        sys.exit(255)
    return str(key["SecretKey"])

def getCardPin():
    numLines = 0
    for line in open(cardFilePath):
        cardPin = line
        numLines += 1
    
    if numLines > 1:
        print >> sys.stderr, "WARNING: More than 1 line in cardFile"
        sys.stdout.flush()
        sys.exit(255)
    return cardPin

def main():
    #Getting here implies all pre-requisites have been met (NOT FINISHED!)
    accountName = options.a
    ipAddress = options.i
    port = int(options.p)

    request = {}
    response = {}
    request["accountName"] = accountName
    request["pin"] = getCardPin()
    response["account"] = accountName
    if options.n:
        request["action"] = "new"
        request["amount"] = float(options.n)
        response["initial_balance"] = float(options.n)
    elif options.d:
        request["action"] = "deposit"
        request["amount"] = float(options.d)
        response["deposit"] = float(options.d)
    elif options.w:
        request["action"] = "withdraw"
        request["amount"] = float(options.w)
        response["withdraw"] = float(options.w)
    elif options.g:
        request["action"] = "get"

    request = {"request" : request}
    print >> sys.stderr, request
    sys.stdout.flush()
    message = NetMsg(request)
    encodedMessage = message.encryptedJson(getAuthKey(), message.getJson())

    # Create socket and send data to bank
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ipAddress, port))
        sock.sendall(encodedMessage)

        sock.settimeout(10.0)
        received = sock.recv(1024)
        sock.settimeout(None)
        if int(received) == 419:
            sys.exit(255)
        elif received == "transaction_completed":
            print json.dumps(response)
            print "dude!!!"
            sys.stdout.flush()
        elif received == "transaction_failed":
            sys.exit(255)
        elif received == "protocol_error":
            sys.exit(63)
    except socket.error, e:
        print >> sys.stderr, e
        sys.stdout.flush()
    except ValueError:
        pass
    finally:
        sock.close()

    print >> sys.stderr, "Finished"
    sys.stdout.flush()

if __name__ == "__main__":
    main()
        
    
