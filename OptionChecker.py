import re

class OptionChecker:
    @staticmethod
    def regExpChecker(checkedArray):
        if checkedArray[0] != "":
            return False
        if len(checkedArray) > 2:
            return False
        if len(checkedArray) == 2 and checkedArray[1] != "":
            return False
        return True
    
    @staticmethod
    def checkInteger(intString):
        checkedArray = re.split("0|[1-9][0-9]*", intString)
        if not OptionChecker.regExpChecker(checkedArray):
            return False
        return True
    
    @staticmethod
    def checkFloat(floatString):
        checkedArray = re.split("0\.[0-9]{2}|[1-9][0-9]*\.[0-9]{2}", floatString)
        if not OptionChecker.regExpChecker(checkedArray):
            return False
        if float(floatString) < 0.00 or float(floatString) > 4294967295.99:
            return False
        return True
    
    @staticmethod
    def checkFileName(fileNameString):
        checkedArray = re.split("[_\-\.0-9a-z]+", fileNameString)
        if not OptionChecker.regExpChecker(checkedArray):
            return False
        if fileNameString == "." or fileNameString == "..":
            return False
        if len(fileNameString) < 1 or len(fileNameString) > 255:
            return False
        return True
    
    @staticmethod
    def checkAccountName(accountNameString):
        checkedArray = re.split("[_\-\.0-9a-z]+", accountNameString)
        if not OptionChecker.regExpChecker(checkedArray):
            return False
        if len(accountNameString) < 1 or len(accountNameString) > 250:
            return False
        return True
    
    @staticmethod
    def checkIPAddress(ipAddressString):
        ipAddressString = ipAddressString.split(".")
        for number in ipAddressString:
            if not OptionChecker.checkInteger(number):
                return False
            try:
                number = int(number, base=10)
                if number < 0 or number > 255:
                    return False
            except ValueError:
                return False
        return True
    
    @staticmethod
    def checkPortNumber(portNumber):
        # if type(portNumber) is not int:
            # print "This is working"
            # return False
        if portNumber < 1024 or portNumber > 65535:
            return False
        return True
        
            
        