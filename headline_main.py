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
5. Create an interface for finding word lists and selecting them.  User should be able to pick and choose

6. Work on turning partial solves and indeterminate lines into complete solves
7. What if we can't get 2 reasonable solves using setSolve?
8. Test the best threshold for singlesettrim
9. Test to see if it's worth always running singleSetTrim before the thorough version, alternatively
   find a good way to determine how long it'll take, this could be a significant speedup



NOTES:
11/21/17: Ran several tests comparing setSolve with removeSingles on/off, only on strings that contained only valid
		  words.  Interestingly, in 170 test cases, 112 cases contained only words in our dictionary.  This seems
		  like a respectable number.

		  Performance was as follows: 
		  	Singles off completed in 9.92958331108 seconds
		  	Singles on  completed in 9.87210416793 seconds, and removed 1098 more values than singles off
		  	Total extraneous values (singles off) was 20545, singles on had 19447

		  So it looks like setSolve is always better with singleremoval enabled, the option to turn it off
		  will be removed.  

		  Next tried to determine what percentage of "solvable" encoded strings set solve is effective on.
		  Of the 112 cases tried, only 37 had fewer than 10 extraneous values. Less than 10 extraneous values
		  is an extremely close solve, but that's only 37/170 cases where set solve alone works well- far below
		  the 40% goal of 68/170.  It's fast enough that it's always worth trying initially, but we're going
		  to have to see if singleSetTrim can improve performance

		  For single set trim to work, we need to select words that have relatively few matches and ones that share
		  the most characters with other words in the string.  Tests should be run to determine the relative importance
		  of each of these traits.

		  Just completed a round of tests on singleSetTrim_thorough vs setSovler.  As expected, sSTt is much 
		  slower than setSolver, but it solved considerably more lines, in the same 112 case set:

			Trim Time:  66.22738718986511
			Sets Time:  9.911092281341553
				Trim had  9349 extraneous and 58 perfect or near perfect solves
				Sets had  19447 extraneous and 36 perfect or near perfect solves

				NOTE: this was with maxListLen = 500

			With max list length 750
			Trim Time:  80.9944908618927
			Sets Time:  9.914267301559448
				Trim had  8650 extraneous and 59 perfect or near perfect solves
				Sets had  19447 extraneous and 36 perfect or near perfect solves
			
			With max list length 250
			Trim Time:  26.628820180892944
			Sets Time:  9.73991870880127
				Trim had  11401 extraneous and 55 perfect or near perfect solves
				Sets had  19447 extraneous and 36 perfect or near perfect solves

			With max list length 100
			Trim Time:  13.961133003234863
			Sets Time:  9.877316951751709
				Trim had  14890 extraneous and 46 perfect or near perfect solves
				Sets had  19447 extraneous and 36 perfect or near perfect solves

		  Fun fact! Apparently using singSetTrim instead of sSTt in the selectWords2Trim function yields the 
		  same results as set solver.  Same number of extraneous solves, same number of good solves, but in
		  slightly more than twice the time.

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
		
		if self.sDict == None:
			return

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


def selectWords2Trim(encStr,patDict):
	# This function will try several methods to determine which words are eligible for
	# singleSetTrim/singleSetTrim_thorough.
	# Word stats-> numCharacters, numSharedCharacters, numMatches, 
	# First challenge, eliminate any words that share no characters with other words
	
	maxListLen = 100

	#print(encStr)
	start = time.time()
	words = encStr.split(' ')
	while "" in words:
		words.remove("")

	matches = []
	for i in range(0,len(words)):
		matches.append(getMatches(words[i],patDict))
		#print(words[i],"->",len(matches[i]),"matches")

	# Try an initial shakedown process, basically just running setSovle:
	# this is straight from setSolve
	matches = setSolve_slim(words,matches)

	# TODO: improve this ranking process.  Speed is probably more important than
	# 		precision here, so simple is better
	stats = []
	for i in range(0,len(words)):
		shared = 0
		cSet = set(words[i])
		
		for j in range(0,len(words)):
			if i == j:
				continue

			tSet = set(words[j])
			shared += len(tSet & cSet)

		stats.append((i,shared))

	#print(stats)
	stats = sorted(stats,key=lambda s: s[1])[::-1]
	#print("post sort: ",stats[::-1])

	# Remove any words that are unlikely to be useful:
	fstats = []
	for stat in stats:
		if len(matches[stat[0]]) < maxListLen:
			# Ignore any words that are too short
			if len(words[stat[0]]) > 2:
				if stat[1] > 2:
					fstats.append(stat)


	#print("trimming\n")
	# After every iteration, try running getSets again:
	for i in range(0,len(fstats)):
		#print("trying:", words[stats[i][0]])
		if len(matches[fstats[i][0]]) > maxListLen:
			# skip any that will take too long
			continue
		matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
		#matchList = singleSetTrim(words,matches,fstats[i][0],1)
		matches[fstats[i][0]] = matchList
		matches = setSolve_slim(words,matches)


	# Try a second pass- eventually want to replace this with a loop
	for i in range(0,len(fstats)):
		#print("trying:", words[stats[i][0]])
		if len(matches[fstats[i][0]]) > maxListLen:
			# skip any that will take too long
			continue
		matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
		#matchList = singleSetTrim(words,matches,fstats[i][0],1)
		matches[fstats[i][0]] = matchList
		matches = setSolve_slim(words,matches)

	stop = time.time()
	#print("FINISHED! in ", stop-start,"seconds")
	#for i in range(0,len(words)):
	#	print(words[i],"->",len(matches[i]),"matches")
	#	if len(matches[i]) <5:
	#		print("\t",matches[i])	
	#print("######################\n")

	val = getSets(words,matches)
	return val[1]








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

	# Get only test strings for which all words are in the dictionary
	tencStrs = []
	tclrStrs = []
	for test in tests:
		for i in range(0,len(test.encStrs)):
			clrWords = test.clrStrs[i].split(" ")
			while "" in clrWords:
				clrWords.remove("")

			valid = True
			for word in clrWords:
				if findFull(word,tree):
					pass
				else:
					valid = False
					break
			if valid == True:
				tencStrs.append(test.encStrs[i])
				tclrStrs.append(test.clrStrs[i])

	print("From ",len(tests)*5,"test cases, found",len(tencStrs),"which should be solvable")
	print("Trying set solver on all cases:")

	threshold = 10
	goodsolves = 0
	badsolves = 0
	ttrim = 0
	tsets = 0

	Textra = 0
	Sextra = 0
	tsolved = 0
	ssolved = 0

	for testStr in tencStrs:
		t1 = time.time()
		ret = selectWords2Trim(testStr,patDict)
		t2 = time.time()
		ttrim += t2-t1
		tmp = 0
		for key in ret:
			if len(ret[key]) != 1:
				tmp += len(ret[key]) - 1
				Textra += len(ret[key]) - 1
		if tmp < 10:
			tsolved+=1

		t1 = time.time()
		ret = setSolve(testStr,patDict)
		t2 = time.time()
		tsets += t2-t1
		tmp = 0
		for key in ret:
			if len(ret[key]) != 1:
				tmp += len(ret[key]) - 1
				Sextra += len(ret[key]) - 1
		if tmp<10:
			ssolved +=1

		#if extra > threshold:
		#	for key in ret:
		#		print(key,len(ret[key]),ret[key])
		#	print("\n##################\n")
		#	badsolves += 1
		#else:
		#	goodsolves += 1

	
	print("With max list length 750")
	print("DONE!\n\tTrim Time: ",ttrim,"\n\tSets Time: ",tsets)
	print("\t\tTrim had ",Textra,"extraneous and", tsolved,"perfect or near perfect solves")
	print("\t\tSets had ",Sextra,"extraneous and", ssolved,"perfect or near perfect solves")
	#print("Of ",len(tencStrs),"strings tested ", goodsolves,"strings were below the threshold of",threshold)


	'''
	# Runs single set solver on all tests
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