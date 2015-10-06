#!/usr/bin/env python
import sys
import optparse

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
elif options.n == None and options.d == None and options.w == None and not options.g:
    sys.exit(255)

#Check that authFile exists.
try:
    authFile = open(options.s)
except IOError:
    sys.exit(255)

#Check that ipAddress meets specifications
ipAddress = options.i.split(".")
for number in ipAddress:
    try:
        number = int(number, base=10)
        if number < 0 or number > 255:
            sys.exit(255)
    except ValueError:
        sys.exit(255)
    
#Getting here implies all pre-requisites have been met
accountName = options.a
ipAddress = options.i
port = options.p
cardFile = options.c

print "Running atm with the following settings"
print "Account Name is", accountName
print "Bank's IP is", ipAddress
print "Bank's port is", port
print "Authentication file is", authFile
print "Card file is", cardFile
print "Finished"
