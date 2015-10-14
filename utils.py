#!/usr/bin/python
import subprocess
import sys
#from OptionChecker import OptionChecker

class Utils:

	@staticmethod
	def run_command(command):
		p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        shell=True)
		return iter(p.stdout.readline, b'')

	@staticmethod
	def printCmdOutput(command):
		for line in Utils.run_command(command):
			print(line) 


if __name__ == "__main__":
	if(len(sys.argv)>=2):
		command = sys.argv[1]
		if command == "clean":
			Utils.run_command("rm -rf CardFiles/*")
			Utils.run_command("rm -rf bank.auth")

	# if OptionChecker.checkFileName("love"): 
	# 	print ("love")
	# else:
	# 	print("hate")