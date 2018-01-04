from setupFunctions import getMatches
import time
from copy import copy,deepcopy
class WORD(object):
	def __init__(self,encWord,encWords,patDict,index,matches):
		self.encWord = encWord
		self.index = index
		self.uchars = set(encWord)
		
		if matches == None:
			self.matches = getMatches(encWord,patDict)
		
		self.sChars = list(get_shared_chars(encWords,index))
		self.sigDict = get_char_sigs(self.encWord,self.uchars,self.matches)
		
		(self.signatures,self.lookup) = get_sig_sel(self.encWord,self.sChars,self.matches)

		self.validMatches = set(x for x in range(0,len(self.matches)))

	def validSet(self,pDict):
		# Takes a partial dictionary, and checks to see if it has any words that go with it:
		#print("\tIn ",self.index,"validSet")
		
		# Reset self.signatures- really, really stupid error here
		(self.signatures,self.lookup) = get_sig_sel(self.encWord,self.sChars,self.matches)

		sets = []
		for key in pDict:
			# Do we have that key:
			if key in self.uchars:
				try:
					sets.append(self.sigDict[key][pDict[key]])
				except KeyError:
					# TODO: I'm very suspicious of this, but it could be nothing.
					sets.append(set())


		x = set(x for x in range(0,len(self.matches)))
		for curr in sets:
			x &= curr
			if len(x) == 0:
				#print("\treturning false on",self.index)
				return False

		self.validMatches = x
		#print("\treturning True")
		return True

	def removeSignatures(self):
		valid = {}
		for signature in self.signatures:
			if len(set(self.signatures[signature]) & self.validMatches) >0:
				valid[signature] = self.signatures[signature]

		self.signatures = valid

	#def restore_signatures()
#
class SIGSOLVER(object):
	# TODO: Set this up to run with a collection of words.  Setup should only occur once

	def __init__(self,words, patDict):
		self.workingDict = {'T': 'L', 'Z': 'E', 'N': 'P', 'W': 'O', 'J': 'A', 'S': 'T', 'A': 'I', 'L': 'N', 'E': 'J'}


		start = time.time()
		self.words = []
		# Remove any single character words
		for word in words:
			if len(word) >1:
				self.words.append(word)

		print(self.words)
		# Initialize word objects
		self.WORDS = []
		for i in range(0,len(self.words)):
			self.WORDS.append(WORD(self.words[i],self.words,patDict,i,None))

		# Determine which word has the fewest signatures:
		tst = sorted(self.WORDS,key=lambda s: len(s.signatures))
		stop = time.time()
		print(stop-start)

		#pdict = {'T': 'L', 'Z': 'E', 'N': 'P', 'W': 'O', 'J': 'A', 'S': 'T', 'A': 'I', 'L': 'N', 'E': 'J'}
		#for curr in self.WORDS:
		#	print(curr.index,curr.validSet(pdict))
		#	curr.removeSignatures()
		#	print(curr.signatures)

		# This is going to be a list of setDicts that are valid i.e. have only one char in each position
		self.solutions = []
		usedWords = set()
		#inDict = {'T': 'L', 'Z': 'E', 'N': 'P', 'W': 'O', 'J': 'A', 'S': 'T', 'A': 'I', 'L': 'N', 'E': 'J','R':'S'}
		inDict = {}
		mappedChars = set()
		self.pickNext(tst[0].index,usedWords,inDict,mappedChars)

	def pickNext(self,index,usedWords,inDict,mappedChars):
		# Add the selected signature to the current dictionary
		inUse = set(usedWords)
		inUse.add(index)
		##print("*********************************************")
		##print("new pick next call",index,"len",len(self.WORDS[index].signatures))
		##print()
		for signature in self.WORDS[index].signatures:
			##print("signature:",signature,index)
			sigValid = True
			pDict = deepcopy(inDict)
			uvals = deepcopy(mappedChars)
			
			# Iterate through all mappings assosciated with this signature
			for entry in self.WORDS[index].lookup[signature]:
				if entry in pDict:
					if pDict[entry] == self.WORDS[index].lookup[signature][entry]:
						pass
					else:
						# CONFLICT! This new signature is trying to overwrite an existing entry
						sigValid = False
						break
				else:
					if self.WORDS[index].lookup[signature][entry] not in uvals:
						pDict[entry] = self.WORDS[index].lookup[signature][entry]
						uvals.add(self.WORDS[index].lookup[signature][entry])
					else:
						sigValid = False
						break

			
			##print("pDict",pDict)

			if sigValid == False:
				##print("\tHere?")
				continue
			# confirm that every WORD has a set of valid entries for this dictionary:
			for curr in self.WORDS:
				if curr.validSet(pDict):
					# We're good
					pass
				else:
					# Fault detected, reject this pDict
					##print("\tSignature rejected, no valid sets for ",curr.encWord,curr.index)
					sigValid = False
					break

			if sigValid:
				# This one is good, pick the next one/verify we aren't already done
				if len(inUse) == len(self.WORDS):
					# Really Done
					##print("DONE!")
					for word in self.WORDS:
						print(word.validMatches)
					print(pDict)
					self.solutions.append(deepcopy(pDict))
				else:
					tmpIndexes = []
					for word in self.WORDS:
						word.validSet(pDict)
						word.removeSignatures()

					tst = sorted(self.WORDS,key=lambda s: len(s.signatures))
					xx = 0
					
					for item in tst:

						if item.index not in inUse:

							#for curr in self.WORDS:
							#	curr.validSet(pDict)
							#	curr.removeSignatures()

							if len(item.signatures) == 0:
								for x in tst:
									print(x.signatures)
								print(pDict)
								##print("\tSignatures invalidated!")
								for word in self.WORDS:
									print(word.index, len(word.signatures))
								break

							self.pickNext(item.index,inUse,pDict,uvals)
							##print("\t***********RETURNING UP ONE",index)
							# Reset the WORD OBJECTS to their prior state:
							for curr in self.WORDS:
								curr.validSet(pDict)
								curr.removeSignatures()

					#while True:
					#	if tst[xx].index in inUse:
					#		xx +=1
					#	else:
					#		break
					#self.pickNext(tst[xx].index,inUse,pDict,uvals)

def get_charDicts(encWords,matches):
	# Returns a list containing the sigDicts for each word
	# if an encoded word does not need a charDict (no shared characters, length of 1)
	# then its position in the list will be None
	# Each chardict in the list is: charDict[encChar][clrChar] = set of match indexes

	charDicts = []
	for i in range(0,len(encWords)):
		if len(encWords[i]) < 2:
			charDicts.append(None)
			break
		# TODO: Should this threshold be a 1?
		sChars = list(get_shared_chars(encWords,i))
		if len(sChars) < 2:
			charDicts.append(None)
			break

		charDicts.append(get_char_sigs(encWords[i],sChars, matches[i]))

	return charDicts

def get_sig_sel(encWord, sChars, matches):
	# Given an encoded word, the characters it shares with other words
	# and a list of potential matches, returns a dictionary where the keys 
	# are unique signatures, and the values are the lists of indexes where the 
	# signature occurs

	# Note a signature is a string of the clear characters that the shared characters
	# in a word map to.

	# First determine the positions we want to check:
	positions = []
	for char in sChars:
		positions.append(encWord.find(char))

	# Now produce the dictionary
	sigDict = {}
	lookup = {} # Keeps a list of key value mappings for each signature

	# Iterate through all matches
	for i in range(0,len(matches)):
		# Determine the signature of the match
		tSig = ""
		for pos in positions:
			tSig += matches[i][pos]

		# Add to the dictionary:
		if tSig in sigDict:
			# Entry already appears, append the index to the existing list
			sigDict[tSig].append(i)
		else:
			# Entry does not yet exist, create one			
			sigDict[tSig] = [i]
			tdict = {}
			for p in positions:
				tdict[encWord[p]] = matches[i][p]
			lookup[tSig] = tdict

	return (sigDict,lookup)

def get_char_sigs(encWord,sChars, matches):
	# Same concept as above, but instead we have a nested dictionary
	# where outDict[encChar][clrChar] = set of match indexes

	# First determine the positions we want to check:
	positions = []
	for char in sChars:
		positions.append(encWord.find(char))

	outDict = {}
	for pos in positions:
		outDict[encWord[pos]] = {}


	for i in range(0,len(matches)):

		for pos in positions:
			if matches[i][pos] in outDict[encWord[pos]]:
				# Entry already exists
				outDict[ encWord[pos] ] [ matches[i][pos] ].append(i)
			else:
				# Entry does not yet exist
				outDict[ encWord[pos] ] [ matches[i][pos] ] = [i]

	# Convert all lists to sets:
	# TODO: Time this to figure out if it is actually worth doing
	# 		Compare with the time it takes to do it when we create the 
	#		set as we go

	for key1 in outDict:
		for key2 in outDict[key1]:
			outDict[key1][key2] = set(outDict[key1][key2])

	return outDict

def get_shared_chars(encWords, sel):
	# Given a list of encoded words and a selection, return a list of all the characters in 
	# the selection that appear in at least one other word of length > 1
	# TODO: Experiment with changing the threshold to length > 2
	
	# Get the set of characters in sel
	a = set(encWords[sel])
	tStr = ""
	for i in range(0,len(encWords)):
		if i != sel and len(encWords[i]) > 1:
			tStr += encWords[i]
	# Set of all other characters
	b = set(tStr)

	# Return the intersection of a & b
	return a & b

def get_sig_tuples(encSig, clrSig, tChars):
	# Just creates a list of (encChar,clrChar) tuples
	# encSig is the signature of the selected word
	# clrSig is the signature assosciated with that
	# tChars is a string or list of characters we want to include in 
	# our intersection check

	a = [x for x in encSig]
	b = [x for x in clrSig]
	out = []
	for i in range(0,len(encSig)):
		if encSig[i] in tChars:
			out.append((a[i],b[i]))

	return out	


