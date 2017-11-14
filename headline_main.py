# Primary code for solving headline puzzles:
###########################################################
# TODOs
'''
1. Find a way to make setSolve more fault tolerant
2. Use brute force to try all possible combinations for a given sDict
3. Work on configuration file, and startup process. Should automatically grab whatever files 
   are in the folder and end with pats.p or tree.p
4. Improve set solver by checking for sets containing only one letter and removing that letter from
   all other sets.

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
	def __init__(self,encStr,clrStr):
		pass

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
	
	tests = getTestFiles("testFiles.txt")
	# TODO: Evaluate relative success of each operation, failure(# of empty sets),success(# of non 1 sets), no result(few reductions)
	for test in tests:
		numPassed = 0
		start = time.time()
		for encStr in test.encStrs:
			result = setSolve(encStr,patDict)
			ret = evaluateresult(result)
			if ret == False:
				continue
			else:
				if (ret[0]+ret[1]) > (ret[2] +ret[3]):
					numPassed +=1
		stop = time.time()
		print(test.handle,"Passed ",numPassed,"/5\n\t in ",stop-start,"seconds")
		print("*********************************************\n\n")


	#patDict = buildDict("websters_clean.txt")
	#patDict = buildDict("00Dictionary.txt")
	#tree = buildTree("00Dictionary.txt")

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