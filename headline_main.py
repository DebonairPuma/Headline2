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

After setSolver runs on each, the program will evaluate which headline is going to be the easiest to solve,
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
1. 	Find a way to make setSolve more fault tolerant
2. 	Use brute force to try all possible combinations for a given sDict
3. 	Work on configuration file, and startup process. Should automatically grab whatever files 
   	are in the folder and end with pats.p or tree.p
5. 	Create an interface for finding word lists and selecting them.  User should be able to pick and choose

6. 	Work on turning partial solves and indeterminate lines into complete solves
7. 	What if we can't get 2 reasonable solves using setSolve?
8. 	Test the best threshold for singlesettrim
9. 	Test to see if it's worth always running singleSetTrim before the thorough version, alternatively
   	find a good way to determine how long it'll take, this could be a significant speedup
10. Implement the single chain solver as a a stepping stone on the way to getting
    two complete solves.
11. Prepare handoff between single line solvers and geometric solvers.
12. Polish omitWords method in HEADLINE/evaluate it's performance.  Initial results
	look pretty good tbh

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

			With max list length 10000
			Trim Time:  638.6522572040558 
			Sets Time:  9.727199077606201
				Trim had  6498 extraneous and 63 perfect or near perfect solves
				Sets had  19447 extraneous and 36 perfect or near perfect solves

		  Fun fact! Apparently using singSetTrim instead of sSTt in the selectWords2Trim function yields the 
		  same results as set solver.  Same number of extraneous solves, same number of good solves, but in
		  slightly more than twice the time.

	In find valid signatures, I'm looking at iTuples and noticing that the same sets of tuples
	are coming up several times.  Is there a good way to avoid this?

	TODO: Check intersections should return the set it declared valid
	TODO: Investigate weird results from omitWords. It's occasionally returning
		  bogus words.  See:
				Omitted:  NKRMN
				LA SH _S _O__ SCHOOLS OGPU B_HA__ A__ACK SCAUP
				CO NKRMN XUPB NTKUUCN UJYE DSKOXS OMMOTV NTOEY
				LA SHUTS DOWN SCHOOLS OVER JIHADI ATTACK SCARE		  

				Omitted:  YMJYHEQYGR
				___ ____ __ _______ ____   ______ __ ___ ______ ___ _____
				OAM CEPP YMJYHEQYGR CERW   IYKAGL RD SLI LBHEGX GOP XSQYI
				FOX WILL EXPERIMENT WITH   SECOND TV ADS DURING NFL GAMES

	TODO: 

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
from sigSolver2 import *

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
			"HPQFRC BRFFSRB OQFJ EQIERC TGG MKBBRPDRU"] #UNITED SETTLES WITH KICKED-OFF PASSENGER 

# US DEC 17
encStrs = [	"QBOKHP YCSWDWNRDEJ JDO SHTDWR SHJX FHCX EBN",
			"FIBMX TUDWBJ WPBIE MUPPC POPU PBUIDPU",
			"LWSICNIC VAMGIC WCMBLI YR WE ERMXZ QTQCFL",
			"QHYIC KQCBQ M L LWSRRAL ZIY BXHAMO RH DMICYR CBWQX LYMFIXYL",
			"WJCJQIE FQISC OGQAQY PS C U YJJN PSUQJIYJ PS CIPEV RIV"] 


class HEADLINE(object):
	# An object for storing an encoded headline and some relevant data about it
	# Stats: Number of unique letters
	# Letters by frequency
	# 
	def __init__(self,encStr,patDict,pDict,index):
		# Initialize status variables:
		self.index = index # Keeps track of which line this one is.
		# sDict contains exactly one character for every character in it
		self.solved = False

		# sDict contains some fully solved characters, and no empty sets
		self.partial = False

		# sDict contains one or more empty sets (probably all empty sets)
		# Usually means the encoded string contains an unknown word. omitWords
		# may be able to find a solution.
		self.failed = False

		# sDict contains too many extraneous characters, solution may
		# not be possible via sigSolve or setSolve
		self.incomplete = False

		# encStr is the headline we wish to solve
		# pDict contains any mappings we've already confirmed.
		self.patDict = patDict
		self.encStr = encStr
		self.encWords = encStr.split(" ")
		while "" in self.encWords:
			self.encWords.remove("")

		self.uChars = set(encStr)
		self.uChars.discard(' ')

		self.allMatches = []
		for i in range(0,len(self.encWords)):
			self.allMatches.append(getMatches(self.encWords[i],self.patDict))

		# Run Set Solve
		self.sDict = setSolve(self.encStr,self.patDict)

		# Evaluate sDict and set status accordingly
		self.getStatus()

		if self.failed ==False and self.solved == False:
			# If failed, implies we have an unknown word
			# If not solved, implies sigSolve may yet be effective
			words = self.encStr.split(' ')
			while "" in words:
				words.remove("")

			self.sDict = self.sigSolve(words, self.patDict)
			self.getStatus()

		# Create a partial Dictionary:
		self.generatepDict()

	def omitWords(self,clrStr):
		# Try using sigSolver but omit a single word at a time until success:
		# This is a painfully simple, yet semi effective method for 
		# handling words that aren't in the dictionary
		

		# TODO: This can generate more than one solution.  We need to detect when that
		# 		happens and account for it somehow.  Determine which solution is the 
		# 		best, or which combination is the best
		# How many potential solutions do we have?
		potentialSolves = 0


		words = self.encStr.split(' ')
		while "" in words:
			words.remove("")

		for i in range(0,len(words)):
			# Ignore any words that are length 1 or 2:
			if len(words[i]) > 2:
				wcopy = list(words)
				del wcopy[i]
				self.sDict = self.sigSolve(wcopy,self.patDict)
				self.failed = False
				self.getStatus()

				# TODO: Identify incomplete solves
				if self.failed == False:
					# For now, just keep track of total solutions, and call
					# it a failure if more than one appears
					potentialSolves +=1
					self.generatepDict()
					#print("Omitted: ",words[i])
					#printPartial(self.pDict,self.encStr,True)
					#if clrStr != None:
					#	print(clrStr)
					#print()

		if potentialSolves > 1:
			self.failed = True
			self.partial = False

	def generatepDict(self):
		# Converts the current sDict into a pDict
		self.pDict = {}
		#print("generating pdict")
		#print(self.sDict)
		for key in self.sDict:
			try:
				items = list(self.sDict[key])
				if len(items) == 1:
					self.pDict[key] = items[0]
				else:
					self.pDict[key] = '_'
			except TypeError:
				self.pDict[key] = '_'
		#print(self.pDict)
		#print("done")

	def getStatus(self):
		# Evaluates sDict, if all entries map to exactly one letter, then 
		# Solved is set to True
		# If one or more sets has exactly one entry then partialSolved
		# If one or more sets has zero, then failed
		
		# Number of unique characters in string
		uChars = len(self.sDict.keys())

		self.numSolved = 0
		self.numFailed = 0
		
		if self.sDict == None:
			return

		for key in self.sDict:
			if len(self.sDict[key]) == 0:
				self.numFailed += 1
			elif len(self.sDict[key]) == 1:
				self.numSolved += 1

		# Reset variables:
		self.solved = False
		self.partial = False
		self.failed = False
		self.incomplete = False

		if self.numFailed > 0:
			self.failed = True
		elif self.numSolved >= 0:
			self.partial = True
			if self.numSolved == uChars:
				self.solved = True
		else:
			self.incomplete = True

	def sigSolve(self,words,patDict):
		# This function will try several methods to determine which words are eligible for
		# singleSetTrim/singleSetTrim_thorough.
		# Word stats-> numCharacters, numSharedCharacters, numMatches, 
		# First challenge, eliminate any words that share no characters with other words
		
		maxListLen = 10000

		#print(encStr)
		#start = time.time()


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
			#matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
			ss = SigSolver(words,matches)
			matchList = ss.sigTrim(fstats[i][0])
				
			matches[fstats[i][0]] = matchList
			matches = setSolve_slim(words,matches)


		# Try a second pass- eventually want to replace this with a loop
		for i in range(0,len(fstats)):
			#print("trying:", words[stats[i][0]])
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue
			#matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
			#matchList = singleSetTrim(words,matches,fstats[i][0],1)
			ss = SigSolver(words,matches)
			matchList = ss.sigTrim(fstats[i][0])

			matches[fstats[i][0]] = matchList
			matches = setSolve_slim(words,matches)

		#stop = time.time()
		#print("FINISHED! in ", stop-start,"seconds")
		#for i in range(0,len(words)):
		#	print("\t",words[i],"->",len(matches[i]),"matches")
		#	if len(matches[i]) <5:
		#		print("\t\t",matches[i])	
		#print("######################\n")

		val = getSets(words,matches)
		return val[1]

	def getChains(self):
		# Calls the getChains function with the current pDict
		self.chains = getChains(self.pDict)

	def checkSol(self):
		# calls printPartial:
		printPartial(self.pDict,self.encStr,True)

def SOLVER(encStrs,patDict,tree):
	# This is the main function for solving the puzzle for each month.  Keeps
	# everything organized and makes calls to working functions.
	headlines = []
	start = time.time()
	# First, initialize all of the headlines
	for i in range(0,len(encStrs)):
		headlines.append(HEADLINE(encStrs[i],patDict,None,i))
	stop = time.time()
	print("Finished initialization in: ", stop-start)

	# Check statuses for each line, add full or partial solves to one list
	# and failed/incomplete to another
	goodLines = []
	badLines  = []
	for headline in headlines:
		if headline.solved == True or headline.partial == True:
			goodLines.append(headline)
		else:
			badLines.append(headline)


	# Go ahead and try this on all lines, it's probably worth while
	# TODO: Experiment with this threshold, is it faster to go straight to 
	# 		grids?
	#if len(goodLines) < 2:
		# Try running omitWords on remaining lines:		
	for headline in badLines:
		headline.omitWords(None)
		if headline.partial == True:
			goodLines.append(headline)

	# Assuming omitLines got us up over that threshold, start getting chains
	print("Found: ",len(goodLines),"partial solutions.  Generating grids\n")

	# Get a list of all the chains we have available, and create the best possible
	# grid based on them.  Then apply that grid to everything in badLines
	chains = []
	for headline in goodLines:
		headline.getChains()
		if len(headline.chains) < 2:
			pass
		else:
			#headline.checkSol()
			#print(headline.chains)
			chains.append(headline.chains)

	if len(chains)< 2:
		# In the future, this should dump us into manual solving mode
		print("ABORTING! couldn't get enough partial solutions to generate a graph!")
		return False
	

	# Determine which pair of chains produces the largest set

	indexes = [x.index for x in goodLines]

	combos = []
	while len(indexes) > 1:
		curr = indexes.pop()
		for index in indexes:
			res = largestSets(headlines[curr].chains,headlines[index].chains)
			if len(res) == 0:
				continue
			# Sort by largest set:
			res = sorted(res,key=lambda s: s[1])[::-1]

			# Store as: ((indexA,indexB),size,seed)
			
			combos.append(((curr,index),res[0][1],res[0][0][0]))
	
	combos = sorted(combos,key=lambda s: s[1])[::-1]
	print(combos)
	return True

	# Determine which grid is best:
	#tg = GRID(26,chains[0],chains[1],13,None)
	#tg.printGrid()


	#for i in range(0,len(encStrs)):
	#	print("Line: ",i)
	#	printPartial(headlines[i].pDict,encStrs[i],True)
	#	print()
	#for i in range(0,len(encStrs)):
	#	print("Omitted version:",i)
	#	headlines[i].omitWords(None)



def largestSets(listA,listB):
	# Takes two lists of chains, A and B
	# First, determine which items in A and B are linked
	# Then, if more than one set of items are linked, determine which is best
	setA = set(listA)
	setB = set(listB)

	# returns results, which is a list of tuples (Chain from A, Super Set Length)
	results = []

	while len(setA) != 0:
		currS = set()
		changes = 1

		# Pull an item from A		
		tmp = setA.pop()
		
		# Add it to current set:
		currS |= set(tmp)

		# Iterate through 
		while changes > 0:
			changes = 0
			toDiscard = []
			for item in setB:
				if len(currS & set(item)) >0:
					toDiscard.append(item)
					#setB.discard(item)
					currS |= set(item)
					changes += 1

			for x in toDiscard:
				setB.discard(x)

			toDiscard = []
			for item in setA:
				if len(currS & set(item)) >0:
					toDiscard.append(item)
					#setA.discard(item)
					currS |= set(item)
					changes += 1

			for x in toDiscard:
				setA.discard(x)
		# Append results:
		results.append((tmp,len(currS)))
	return results

'''
#Test Chains:
mar17
['ARTOKNLPS', 'BD', 'CZ', 'EM', 'FQIUWY', 'HX']
['ANLPSGMEVRTO', 'BD', 'HZ', 'IUW', 'JY']
['AZ', 'CSIEN', 'DO', 'FMWP', 'GU', 'HLQR', 'TX']
['AY', 'BLUT', 'CE', 'DPWR', 'GH', 'INJO', 'MZ']

feb17
['AFR', 'BD', 'CSEY', 'GL', 'HI', 'KM', 'NPW', 'TU']
['ALIXY', 'BS', 'CT', 'DOPU', 'ERM', 'FG']
['ABCE', 'DLKR', 'HP', 'INWO', 'TY']
'''


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


	'''
	# Run only first part on difficult headlines.  Used to improve omitWords
	diffEncStrs = pickle.load(open("DifficultEncodedStrings.p","rb"))
	diffClrStrs = pickle.load(open("DifficultClearStrings.p","rb"))
	print(len(diffEncStrs))
	for i in range(0,len(diffEncStrs)):
		H = HEADLINE(diffEncStrs[i],patDict,None)
		H.omitWords(diffClrStrs[i],patDict)
	'''
	print(largestSets(['ARTOKNLPS', 'BD', 'CZ', 'EM', 'FQIUWY', 'HX'],['ANLPSGMEVRTO', 'BD', 'HZ', 'IUW', 'JY']))

	


	
	# Full tests:
	passed = 0
	failed = 0
	for test in tests:
		# Setup all headline objects
		print("\nStarting:",test.handle)
		start = time.time()
		ans = SOLVER(test.encStrs,patDict,tree)
		stop = time.time()
		print("Finished in: ", stop-start)
		if ans:
			passed+=1
		else:
			failed+=1

	print("passed:",passed,"failed:",failed)

		#for i in range(0,len(test.encStrs)):
			#print("Line: ",i)
			#printPartial(headlines[i].pDict,test.encStrs[i],True)
			#print(test.clrStrs[i])
			#print()
	

	
	# SOLVE SINGLE HEADLINE SET
	'''
	headlines = []
	start = time.time()
	for line in encStrs:
		headlines.append(HEADLINE(line,patDict,None))
	stop = time.time()
	print("Finished initialization in: ", stop-start)
	for i in range(0,len(encStrs)):
		print("Line: ",i)
		printPartial(headlines[i].pDict,encStrs[i],True)
		print()
	for i in range(0,len(encStrs)):
		print("Omitted version:",i)
		headlines[i].omitWords(None)
	'''

if __name__ == '__main__':
	main()