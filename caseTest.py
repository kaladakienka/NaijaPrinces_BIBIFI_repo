#!/usr/bin/python

import subprocess
import sys
from utils import Utils
# def run_command(command):
#     p = subprocess.Popen(command,
#                          stdout=subprocess.PIPE,
#                          stderr=subprocess.STDOUT,shell=True)
#     return iter(p.stdout.readline, b'')

# def runTest(command):
# 	for line in run_command(command):
#     		print(line)

#print "%s" % run_command("echo love")

tnum = sys.argv[1]
if tnum == "0":#correct
	command = "python atm.py -a abc0 -n 10.30"
elif tnum == "01":#correct
	command = "python atm.py -a abc0 -d 5.00"	
elif tnum == "02":#correct
	command = "python atm.py -a abc0 -g"		
elif tnum == "1": #correct
	command = "python atm.py -a abc1 -n 10000.00"
elif tnum == "2": #invalid balance format : negative
	command = "python atm.py -a abc2 -n -10000.00"
elif tnum == "3":#invalid balance format : more than 2 decimal places
	command = "python atm.py -a abc3 -n 10000.044"
elif tnum == "4":#invalid balance format : leading zeros
	command = "python atm.py -a abc4 -n 010000.04"
elif tnum == "5":#invalid balance format : hex
	command = "python atm.py -a abc5 -n 0x2a"
elif tnum == "6":#invalid balance format : too large number
	command = "python atm.py -a abc6 -n 4294967296.99"
elif tnum == "7":#invalid balance format : zero
	command = "python atm.py -a abc7 -n 0.00"	
elif tnum == "8":#invalid filename format : dot
	command = "python atm.py -s . -a abc8 -n 10.00"	
elif tnum == "9":#invalid filename format : dot dot
	command = "python atm.py -s .. -a abc9 -n 10.00"	
elif tnum == "10":#invalid filename format : @
	command = "python atm.py -s @l.v -a abc10 -n 10.00"
elif tnum == "11":#invalid filename format : exclamation
	command = "python atm.py -s !.v -a abc11 -n 10.00"
elif tnum == "12":#invalid filename format : capital
	command = "python atm.py -s _.V -a abc12 -n 10.00"
elif tnum == "13":#invalid ip4 format : idk
	command = "python atm.py -s _.V -i 1.193.3333.255 -a abc13 -n 10.00"
elif tnum == "14":#invalid port format : too small
	command = "python atm.py -s _.V -i 1.193.3333.255 -p 1023 -a abc14 -n 10.00"
elif tnum == "15":#invalid port format : too large
	command = "python atm.py -s _.V i 1.193.3333.255 -p 65536 -a abc15 -n 10.00"

Utils.printCmdOutput(command)

# Utils.printCmdOutput("rm -rf CardFiles/*")
#runTest("rm -rf CardFiles/index")
