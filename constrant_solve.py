from constraint import *
from setupFunctions import *
from sigSolver import get_char_sigs,get_shared_chars
#import pickle
from TestingFuncs import *
from searchTree import *
from setSolver import *
import time



class WORD(object):
	def __init__(self,encWord,patDict,index,encWords):
		self.encWord = encWord
		self.uchars = set(encWord)
		self.index = index
		
		self.encChars = list(self.uchars)

		self.matches = getMatches(encWord,patDict)
		self.charDict = get_char_sigs(self.encWord,self.uchars,self.matches)

		self.sharedChars = list(get_shared_chars(encWords,self.index))


	def checkSet(self,*inChars):
		# Function called by constraint solver, returns T/F based on whether or not
		# the enc->clr mapping has words
		# clrChars is a list in the same order as self.encChars
		#assert len(clrChars) == len(self.encChars)
		#print self.encWord
		#print inChars
		clrChars = list(inChars)
		#print clrChars
		#exit()
		sets = []
		for i, cChar in enumerate(clrChars):
			try:
				sets.append(self.charDict[self.encChars[i]][cChar])
			except KeyError:
				# That mapping does not exist, return False
				return False

		# Check intersection of all sets:
		x = set(sets[0])
		for curr in sets:
			x &= curr
			if len(x) == 0:
				return False

		return True

	def checkSet2(self,*inChars):
		# Same as above, but looks only at shared chars
		clrChars = list(inChars)
		#print clrChars
		#exit()
		sets = []
		for i, cChar in enumerate(clrChars):
			try:
				sets.append(self.charDict[self.sharedChars[i]][cChar])
			except KeyError:
				# That mapping does not exist, return False
				return False

		# Check intersection of all sets:
		x = set(sets[0])
		for curr in sets:
			x &= curr
			if len(x) == 0:
				return False

		return True		


def main():
	# Import Pickled patDict and tree
	sources = ["00english.txt",
			   "00english1.txt",
			   "00english2.txt",
			   "00english3.txt"]

	tree = None

	for source in sources:
		tree = buildTree(source,tree)

	patDict = None

	for source in sources:
		patDict = buildDict(source,patDict)

	print "built dict and tree"

	tests = getTestFiles("testFiles.txt")
	alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
		
	for test in tests:
		for encStr in test.encStrs:
			try:
				start = time.time()
				#printPartial({'A': 'I', 'C': 'Y', 'E': 'J', 'D': 'U', 'G': 'T', 'K': 'G', 'J': 'A', 'L': 'N', 'O': 'F', 'N': 'P', 'Q': 'V', 'P': 'M', 'S': 'S', 'R': 'R', 'T': 'L', 'W': 'O', 'V': 'H', 'Z': 'E'},encStr,True)
				words = encStr.split(" ")
				while " " in words:
					words.remove(" ")

				WORDS = []
				for i in range(0,len(words)):
					WORDS.append(WORD(words[i],patDict,i,words))


				charSet = set(encStr)
				charSet.discard(" ")

				# standard: 5.2535340786
				# Backtracking: 5.24119997025
				# Recursive: 5.19842505455
				# Min Conflicts: ~8.2


				prob = Problem(RecursiveBacktrackingSolver())
				# TODO: limit the domains ahead of time?
				matches = []
				for i in range(0,len(words)):
					matches.append(getMatches(words[i],patDict))
				

				#get_shared_chars(encWords, sel)
				

				ret = getSets(words,matches)
				sDict = ret[1]
				
				# Only use variables that appear in multiple words:
				str_shared_chars = set()
				for curr in WORDS:
					str_shared_chars |= set(curr.sharedChars)

				for key in str_shared_chars:
					prob.addVariable(key,list(sDict[key]))
				#prob.addVariables(list(charSet),alpha)
				prob.addConstraint(AllDifferentConstraint())

				# Add word constraints:
				for curr in WORDS:
					if len(curr.sharedChars) > 0:
						prob.addConstraint(curr.checkSet2,curr.sharedChars)
				print len(charSet)
				print "Setup done"
				#exit()
				#printPartial(prob.getSolution(),encStr,True)
				
				sols =  prob.getSolutions()
				for sol in sols:
					printPartial(sol,encStr,True)
				
				#print sols, len(sols)
				stop = time.time()
				print stop-start
			except:
				print "exception"
				pass











if __name__ == '__main__':
	main()