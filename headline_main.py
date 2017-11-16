'''
# Primary code for solving headline puzzles:
Outline of Excecution:
If no arguments are passed to the solver, it should first look for a puzzle file which will be a text file
with the encoded headlines pasted in.

Next, the program will look for the tree and pattern files ".p" and load them in, if none are 
available, or arguments are passed to the program, it will look for dictionaries and manually build them
After these are built, the program will check the customWords file and add anything appearing there to
the pattern dict and search tree

Next, the program will initialize the HEADLINE objects by passing them each an encoded string.  These 
objects will break the string into words, find matches for each word from the pattern dict, and then run
setSolver

After setSolver runs on each, the program will evaluate which healine is going to be the easiest to solve,
and will use some combination of thorough solve to try and get a full solution
	A line is fully solved when sDict contains a single character for each encoded character

Hopefully, the program will manage to completely solve at least two of the headlines.  If this occurs, we'll 
gather chains and build a grid to attempt to solve the remaining headlines.

This process will continue until we have a full 26 character long string.  At this point, it's probably worth
using the grid to verify that the solutions for each headline are correct, TODO: need to find a way to 
search for errors and at least notify the user that they've occured

Once the 26 long string is found, we'll attempt to extract the setting, key, and hat.

'''
###########################################################



# TODOs
'''
1. Find a way to make setSolve more fault tolerant
2. Use brute force to try all possible combinations for a given sDict
3. Work on configuration file, and startup process. Should automatically grab whatever files 
   are in the folder and end with pats.p or tree.p
4. Improve set solver by checking for sets containing only one letter and removing that letter from
   all other sets.
5. Create an interface for finding word lists and selecting them.  User should be able to pick and choose

6. Work on turning partial solves and indeterminate lines into complete solves

'''

###########################################################
# IMPORTS
import sys
import time
import pickle
from setupFunctions import *
from grids import cell, GRID
from setSolver import *
from retrieveKey import *
from searchTree import *
from TestingFuncs import *

###########################################################
# CONFIGURATION
sourceDict = "websters_clean.txt"

encStrs = ["DMXWPMKH NGQCB CPLK DYBF ULKHGRGLKMP LF RL ELXC TWACXPLLA RYKKCP",
		   "AKFQO SGWDA CG GTAC FOB UDKNFHD HFCFNFO NDFBDUA",
		   "ST OHSKWASIDK EIWDS NQH MEHHWBLIS HSJWSN",
		   "ZUAAUF EPWFTE WMCUDX FPXU PF XRU UYPFPHZ",
		   "PMF RKEEODDOKPTW TPRKXWBLTD YTBED YK WTDKFIT YUTOW SWKYTDY ODDXTD"]
encStrs = [	"LMWQLX NRQSKV QY SKXMLINVML ZLNHHMH LMEQLVMX OK JNG",
			"DXGUX NHQHAQ CHIHAYWP VYQX GXYW RCM",
			"UEA ITKZ JPZVPZZTZ E FTPYYS PRZ ZRWF",
			"UCF CMJCZMJCU RH GOSFQX HMGXU GRDQN O HMXU VDYV",
			"HPQFRC BRFFSRB OQFJ EQIERC TGG MKBBRPDRU"]

class HEADLINE(object):
	# An object for storing an encoded headline and some relevant data about it
	# Stats: Number of unique letters
	# Letters by frequency
	# 
	def __init__(self,encStr,patDict,pDict):
		# encStr is the headline we wish to solve
		# pDict contains any mappings we've already confirmed.
		self.encStr = encStr
		self.encWords = encStr.split(" ")
		while "" in self.encWords:
			self.encWords.remove("")

		self.uChars = set(encStr)
		self.uChars.discard(' ')

		self.allMatches = []
		for i in range(0,len(self.encWords)):
			self.allMatches.append(getMatches(self.encWords[i],patDict))

		# Run Set Solve
		self.sDict = setSolve(self.encStr,patDict)

		# Evaluate sDict and set status accordingly
		self.getStatus()

	def getStatus(self):
		# Evaluates sDict, if all entries map to exactly one letter, then 
		# Solved is set to True
		# If one or more sets has exactly one entry then partialSolved
		# If one or more sets has zero, then failed
		self.numSolved = 0
		self.numFailed = 0
		self.numPartial = 0

		for key in self.sDict:
			if len(self.sDict[key]) == 0:
				self.numFailed += 1
			elif len(self.sDict[key]) == 1:
				self.numSolved += 1
			else:
				self.numPartial += 1

		if self.numSolved == len(self.encWords):
			self.solved = True
		if self.numFailed > 0:
			self.failed = True
			


def main():
	# Check for input arguments
	if len(sys.argv) > 1:
		# Startup in manual mode
		print(str(sys.argv))
		patDict = buildDict(sourceDict,None)
		tree = buildTree(sourceDict,None)

		# Format the name
		tmp = sourceDict[::-1]
		tmp = tmp[4:]
		tmp = tmp[::-1]
		pickle.dump(patDict,open(tmp+"_pats.p","wb"))
		pickle.dump(tree,open(tmp+"_tree.p","wb"))

	
	# Import Pickled patDict and tree
	print("Unpickling Tree and PatDict...")
	start = time.time()
	patDict = pickle.load(open("AllEng_pats.p","rb"))
	tree = pickle.load(open("AllEng_tree.p","rb"))
	stop = time.time()
	print("\tDone in:",stop-start,"seconds")
	

	# Load any special words from file, for now this is all the words that showed up in 
	# the test cases, but weren't already in the list.  This is kind of cheating...
	#print("Loading custom words from file")
	#patDict = buildDict("customWords.txt",patDict)
	#tree = buildTree("customWords.txt",tree)

	# Load up the test files
	tests = getTestFiles("testFiles.txt")
	
	# Pick just one for now:
	test = tests[1]



	for test in tests:
		headlines = []
		start = time.time()
		for i in range(0,len(test.encStrs)):
			headlines.append(HEADLINE(test.encStrs[i],patDict,None))
			for k in range(0,len(headlines[-1].encWords)):
				singleSetTrim_thorough(headlines[-1].encWords,headlines[-1].allMatches,k,1)
	
		stop = time.time()
		print("\tSet up headlines in:",stop-start,"seconds")


		#for i in range(0,len(test.encStrs)):
		#	print(test.clrStrs[i])	




	'''
	log = open("hardlines.txt","w")
	for test in tests:
		numPassed = 0
		start = time.time()
		for i in range(0,len(test.encStrs)):
			result = setSolve(test.encStrs[i],patDict)
			ret = evaluateresult(result)
			if ret == False:
				log.write(test.clrStrs[i]+"\n")
				log.write(test.encStrs[i]+"\n")
				
			else:
				if (ret[0]+ret[1]) > (ret[2] +ret[3]):
					numPassed +=1
		stop = time.time()
		print(test.handle,"Passed ",numPassed,"/5\n\t in ",stop-start,"seconds")
		print("*********************************************\n\n")
	'''
	
	



	'''
	# Attempt to figure out which words just aren't in the dictionary we're using:
	newWords = []
	for test in tests:
		for clrStr in test.clrStrs:
			words = clrStr.split(" ")
			for word in words:
				if findFull(word, tree) == False:
					newWords.append(word)
					print("Couldn't find: ",word)
	
	source = "customWords.txt"
	fp = open(source, "a")
	for word in newWords:
		fp.write(word+"\n")
	fp.close()
	'''

	'''
	#for line in encStrs:
	#	setSolve(line,patDict)
	#tstr = "LMWQLX NRQSKV QY SKXMLINVML ZLNHHMH LMEQLVMX OK JNG"
	tstr = "DXGUX NHQHAQ CHIHAYWP VYQX GXYW RCM"
	matches = []
	encWords = tstr.split(" ")
	for word in encWords:
		matches.append(getMatches(word,patDict))

	for mlist in matches:
		print(len(mlist))

	# Try 3,4,5 with this string
	for item in range(len(encWords)):
		if len(encWords[item])<4:
			continue
		print("Trying word:",encWords[item])
		print("Single Set:")
		ret = singleSetTrim(encWords,matches,item,1)
		if len(ret)<5:
			print(ret)
		print("Thorough:")
		ret = singleSetTrim_thorough(encWords,matches,item,1)
		if len(ret)<5:
			print(ret)
	# Initialize HEADLINE objects
	'''

if __name__ == '__main__':
	main()