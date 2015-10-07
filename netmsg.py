#!/usr/bin/python

import json
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from random import randint

class NetMsg:

	
	def __init__(self, msg):
		self.sessionToken=randint(0,2000)
		self.msgID=randint(0,4000)
		self.msg = msg

	#def __init__(self, sessionToken, msgID, msg):
	#		self.sessionToken = sessionToken
	#		self.msgID = msgID
	#		self.msg = msg

	def incMsgID(self):
			self.msgID = self.msgID +1

	def getMsgID(self):
		return self.msgID

	def setMsgID(self,msgID):
		self.msgID = msgID
	
	def getMsg(self):
		return msg

	def setMsg(self, msg):
		self.msg = msg;

	def getSessionToken(self):
		return self.sessionToken

	def setSessionToken(self,sessionToken):
		self.sessionToken = sessionToken

	def getJson(self):
		data = {}
		data['msgID'] = self.msgID;
		data['sessionToken'] = self.sessionToken
		data['msg'] = self.msg
		json_data =json.dumps(data)

		return json_data
	
	@staticmethod
	def encryptedJson( key, msg):
		#encryption_suite = AES.new(key, AES.MODE_CFB, 'This is an IV456')
		#cipher_text = encryption_suite.encrypt("A really secret message. Not for prying eyes.")
		cipher_suite = Fernet(key)
		cipher_text = cipher_suite.encrypt(msg)

		return cipher_text
	
	@staticmethod
	def decryptJson(key,cipher_text):
		#decryption_suite = AES.new(key, AES.MODE_CBC, 'This is an IV456')
		#plain_text = decryption_suite.decrypt(cipher_text)
		cipher_suite = Fernet(key)
		plain_text = cipher_suite.decrypt(cipher_text)
		return plain_text

	@staticmethod
	def generateKey():
		return Fernet.generate_key()


#netMsg1 =  NetMsg(1000,3000,"blah")
netMsg1 =  NetMsg("blah")
#netMsg1.setMsg("bla")
key = NetMsg.generateKey()
print "key: %s" % key
encMsg = netMsg1.encryptedJson(key,netMsg1.getJson())
decMsg = netMsg1.decryptJson(key,encMsg)
print "%s" % decMsg

# print "%s" % netMsg1.getJson()




