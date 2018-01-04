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


###########################################################
# TODOs

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
from sigSolver_recursive import *

###########################################################
# CONFIGURATION
sourceDict = "websters_clean.txt"

'''
encStrs = ["DMXWPMKH NGQCB CPLK DYBF ULKHGRGLKMP LF RL ELXC TWACXPLLA RYKKCP",
		   "AKFQO SGWDA CG GTAC FOB UDKNFHD HFCFNFO NDFBDUA",
		   "ST OHSKWASIDK EIWDS NQH MEHHWBLIS HSJWSN",
		   "ZUAAUF EPWFTE WMCUDX FPXU PF XRU UYPFPHZ",
		   "PMF RKEEODDOKPTW TPRKXWBLTD YTBED YK WTDKFIT YUTOW SWKYTDY ODDXTD"]
'''
# US JAN 18
encStrs = ["ROLXOND EKDAE NCJDY ZCYD EB OGEDZUOECJDY EB KBSD PDGCJDZI",
		   "JQN VXAA YQHHMH HXCM WU FTJ XH TBFMIJQXB",
		   "AOCGDP GCD PDEDLEBZ EDYEY KOJD OUNGDZY CU LBQZE TOEEGD",
		   "WIANHT LNIG PCRGT GC NUZN PRCTNW GC QRIECYY LNWGJ",
		   "D Q CUJDYECNOEDY CXDO Y PQELK EOF TZDOXY"]

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

	#words = encStrs[4].split(" ")


	#sols = SIGSOLVER(words,patDict)

	#for sol in sols.solutions:
	#	printPartial(sol,encStrs[1],True)
	###################################################################################
	# This is a full test of SOLVER & HEALINE
	# Try solving the latest problem:
	SOLVER(encStrs,patDict,tree)
	#exit()

	aborts = 0
	chainable = 0
	thisMonth = 0
	passed = 0
	diffTests = []

	t1 = time.time()
	for test in tests:
		thisMonth = 0
		for i in range(0,len(test.encStrs)):
			words = test.encStrs[i].split(" ")
			while " " in words:
				words.remove(" ")
			sols = SIGSOLVER(words,patDict)


			print("solution")

			for sol in sols.solutions:
				print(sol)
				printPartial(sol,test.encStrs[i],True)	
			print(test.clrStrs[i])
			exit()	
			'''
			curr = HEADLINE(test.encStrs[i],patDict,None,i)
			while curr.nextState != 'G' and curr.nextState != 'F':
				curr.nextSolve()

			if curr.aborted == True:
				#print("NO SOLUTION")
				#print(test.clrStrs[i])
				diffTests.append((curr,test.clrStrs[i]))
				aborts += 1
			else:
				#print(test.clrStrs[i])
				#curr.checkSol()
				chainable += 1
				thisMonth += 1
			print(test.clrStrs[i])
			curr.checkSol()
			
			print('---------------------------------------------------------------\n')
		if thisMonth > 1:
			passed+=1
		print('**********************************************************************')
			'''

	t2 = time.time()
	'''
	###################################################################################
	# This is a full test of SOLVER & HEALINE
	# Try solving the latest problem:
	SOLVER(encStrs,patDict,tree)

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
	'''

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