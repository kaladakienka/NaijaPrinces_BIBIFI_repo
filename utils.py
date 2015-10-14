#!/usr/bin/python
import subprocess
import sys

class Utils:

	@staticmethod
	def run_command(command):
		p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,shell=True)
		return iter(p.stdout.readline, b'')

	@staticmethod
	def printCmdOutput(command):
		for line in run_command(command):
			print(line) 


if __name__ == "__main__":
	command = sys.argv[1]
	if command == "clean":
		Utils.run_command("rm -rf CardFiles/*")
		Utils.run_command("rm -rf bank.auth")