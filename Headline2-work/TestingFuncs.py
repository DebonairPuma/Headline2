#################################################################################
# Functions for importing test cases/new items
class SOLUTION(object):
	def __init__(self,handle,encStrs,clrStrs,setting,key,hat):
		self.handle = handle
		self.encStrs = encStrs
		self.clrStrs = clrStrs
		self.setting = setting
		self.key = key
		self.hat = hat

def getTestFiles(source):
	testObjects = []
	with open(source,"r") as f:
		num = 1
		encStrs = ["","","","",""]
		clrStrs = ["","","","",""]
		line = f.readline()
		while line != "":
			if num == 1:
				handle = line.upper().strip('\n')
			if num == 2:
				setting = line.upper().strip('\n')
			if num == 3:
				key = line.upper().strip('\n')
			if num == 4:
				hat = line.upper().strip('\n')
			if num == 5:
				clrStrs[0] = processLine(line[3:])
			if num == 6:
				encStrs[0] = processLine(line[3:])
			if num == 8:
				clrStrs[1] = processLine(line[3:])
			if num == 9:
				encStrs[1] = processLine(line[3:])
			if num == 11:
				clrStrs[2] = processLine(line[3:])
			if num == 12:
				encStrs[2] = processLine(line[3:])
			if num == 14:
				clrStrs[3] = processLine(line[3:])
			if num == 15:
				encStrs[3] = processLine(line[3:])
			if num == 17:
				clrStrs[4] = processLine(line[3:])
			if num == 18:
				encStrs[4] = processLine(line[3:])
				testObjects.append(SOLUTION(handle,list(encStrs),list(clrStrs),setting,key,hat))
				#print(handle,setting,key,hat,encStrs,clrStrs)
			line = f.readline()
			num+=1
			if num == 20:
				num = 1

	return testObjects

def processLine(inStr):
	inStr = inStr.upper()
	inStr = inStr.strip('\n')
	makeSpace = set("-1234567890'\\/")
	makeEmpty = set("!:;,.&\"")

	rStr = ""
	for char in inStr:
		if char in makeSpace:
			rStr += " "
		elif char in makeEmpty:
			pass
		else:
			rStr += char
	return rStr

def evaluateresult(sDict):
	perfectSets = 0
	badSets = 0 # > 20
	okSets = 0 # <5 <20
	goodSets = 0 # < 5
	for key in sDict:
		if len(sDict[key]) == 0:
			return False # Total Failure
		elif len(sDict[key]) == 1:
			perfectSets += 1
		elif len(sDict[key]) < 5:
			goodSets += 1
		elif len(sDict[key]) < 20:
			okSets += 1
		else:
			badSets += 1

	return (perfectSets,goodSets,okSets,badSets)