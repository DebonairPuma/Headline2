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

6. 	Work on turning near complete solves into full solves, even if this means querying
	the user
10. Implement the single chain solver as a a stepping stone on the way to getting
    two complete solves.
12. Polish omitWords method in HEADLINE/evaluate it's performance.  Initial results
	look pretty good tbh
13. Develop a method for updating HEADLINE objects with results from grid solver
14. Develop a method for selecting the best grid to use...

15. Make a version of setSolve that takes a set of encoded words rather than a string-
    so we can omit certain words.

16. Low priority- spend some time optimizingn sigSolver

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
from copy import copy
from solver_main import *

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
		headline.omitWords(None,True)
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

	# Use that set to create a grid:
	tg = GRID(headlines[combos[0][0][0]].chains,
			  headlines[combos[0][0][1]].chains,
			  combos[0][2],
			  26,
			  13)
	#tg.printGrid()

	print("extracting chains")
	bestChains = tg.extractChains()
	hChains = bestChains[0]
	vChains = bestChains[1]
	inUse = set([combos[0][0][0],combos[0][0][1]])

	# Get the best existing set size:
	bestSet = combos[0][1]



	# Try to build a better set using the other grids:
	combos = []
	for headline in headlines:
		if headline.index not in inUse:
			headline.getChains()
			res = largestSets(headline.chains,hChains)
			if len(res) != 0:
				res = sorted(res,key=lambda s: s[1])[::-1]
				combos.append(((headline.index,0),res[0][1],res[0][0][0]))

			res = largestSets(headline.chains,vChains)
			if len(res) != 0:
				res = sorted(res,key=lambda s: s[1])[::-1]
				combos.append(((headline.index,1),res[0][1],res[0][0][0]))

	combos = sorted(combos,key=lambda s: s[1])[::-1]

	print("************************************************")
	print("BEFORE UPDATE")
	for curr in headlines:
		if curr.index not in inUse:
			ret = tg.autoSearch(curr.encWords,curr.uChars,tree)
			print("####################################")
			for sol in ret[1]:
				printPartial(sol,curr.encStr,True)
				print()
			print()


	if len(combos)>0:
		if combos[0][1] > bestSet:
			tg = GRID(headlines[combos[0][0][0]].chains,
					  bestChains[combos[0][0][1]],
					  combos[0][2],
					  26,
					  13)
			inUse.add(combos[0][0][0])
			print("New and improved grid:")
			print("inUse:",inUse)
			#tg.printGrid()

			print("************************************************")
			print("AFTER UPDATE")
			# Try the set solver on all headlines that aren't in use:
			for curr in headlines:
				#if curr.index not in inUse:
				ret = tg.autoSearch(curr.encWords,curr.uChars,tree)
				print("####################################")
				for sol in ret[1]:
					print("\t trying tryDict")
					curr.tryDict(sol,False)
					#printPartial(sol,curr.encStr,True)
					
				print()

		else:
			print("Couldn't improve grid!")
			for curr in headlines:
				#if curr.index not in inUse:
				ret = tg.autoSearch(curr.encWords,curr.uChars,tree)
				print("####################################")
				for sol in ret[1]:
					print("\t trying tryDict")
					curr.tryDict(sol,False)
					#printPartial(sol,curr.encStr,True)
					
				print()

	else:
		print("No additional chains available")

	# If additional chains are available, attempt to improve grid
	# otherwise try running grid solve on bad headlines

	return True

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

	###################################################################################
	# Import Pickled patDict and tree
	print("Unpickling Tree and PatDict...")
	start = time.time()
	patDict = pickle.load(open("AllEng_pats.p","rb"))
	tree = pickle.load(open("AllEng_tree.p","rb"))
	stop = time.time()
	print("\tDone in:",stop-start,"seconds")
	
	###################################################################################
	# Load special words from file:
	#print("Loading custom words from file")
	#patDict = buildDict("customWords.txt",patDict)
	#tree = buildTree("customWords.txt",tree)

	# Load up the test files
	tests = getTestFiles("testFiles.txt")

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
	
if __name__ == '__main__':
	main()

'''
	# Run only first part on difficult headlines.  Used to improve omitWords
	diffEncStrs = pickle.load(open("DifficultEncodedStrings.p","rb"))
	diffClrStrs = pickle.load(open("DifficultClearStrings.p","rb"))
	print(len(diffEncStrs))
	for i in range(0,len(diffEncStrs)):
		H = HEADLINE(diffEncStrs[i],patDict,None)
		H.omitWords(diffClrStrs[i],patDict)
'''