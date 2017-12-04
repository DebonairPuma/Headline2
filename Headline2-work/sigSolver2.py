class SigSolver(object):
	def __init__(self,words, matches):

		self.matches = matches
		self.words = words

		# Get the character dictionaries for each other word
		# charDicts[0]->charDict[encChar][clrChar] = set of match indexes
		self.charDicts = get_sigDicts(words,matches)



	def sigTrim(self, tar):
		# tar is the wordlist to trim

		# this is a set of matches that are invalid due to insignificant character
		# mappings
		self.shitSet = set()
		self.tar = tar
		# Get the list of significant characters for selected word:
		selSchars = list(get_shared_chars(self.words, tar))

		# Get the dict of signatures for the selected word
		# selSigs: Keys="clrSig", Values=[matches with that clrSig]
		self.selSigs = get_sig_sel(self.words[tar],selSchars, self.matches[tar])

		# Run find valid signatures:
		ret = self.find_valid_signatures(selSchars, self.selSigs.keys(), self.charDicts)

		# Clean out any matches on the shit list and return the list:

		# Ret is a list of valid signatures, combine the ones that are OK
		# and then fetch the valid matches
		vindexes = []
		out = []
		#print(ret)

		for vsig in ret:
			for index in self.selSigs[vsig]:
				if index not in self.shitSet:
					out.append(self.matches[self.tar][index])

		#print(out)

		return out	

	def find_valid_signatures(self, eSchars, sigsIn, sigDicts):
		# TODO: Once it's easier to understand, try optimizing it.
		# eSchars is a list of encoded shared characters from the target word
		# Checks to see which signatures (if any) are valid
		
		validSigs = []
		setOftChars = set(eSchars)

		sigsIn = list(sigsIn)
		# For every signature, establish a set of subsignatures that we need to apply 
		# to each word:
		# LIST [ DICTS ], where keys are sigTuples, and values are indexes of sigsIn that use
		# that signature

		uSigs = []
		correspondingSigs = []
		for i in range(0,len(sigDicts)):
			if sigDicts[i] == None:
				uSigs.append(None)
				correspondingSigs.append(None)
				continue

			# Get the set of shared characters for this word:
			sEncChars = set(sigDicts[i].keys())
			sEncChars = sEncChars & setOftChars			
			
			# Pass if there are no shared chars
			if len(sEncChars) == 0:
				uSigs.append(None)
				correspondingSigs.append(None)
				continue


			tDict = {}
			tcsd = {}
			for j in range(0,len(sigsIn)):
				iTuple = tuple(get_sig_tuples(eSchars,sigsIn[j], sEncChars))
				if iTuple in tDict:
					# We've already seen this tuple set
					tDict[iTuple].append(j)
					tcsd[iTuple].append(sigsIn[j])
				else:
					# We haven't seen this tuple yet, establish a new list:
					tDict[iTuple] = [j]
					tcsd[iTuple]  = [sigsIn[j]]
			
			uSigs.append(tDict)
			correspondingSigs.append(tcsd)
		
		# Run check intersections on all:
		validSets = []
		for i in range(0,len(sigDicts)):
			if uSigs[i] == None:
				validSets.append(None)
				continue
			if i == self.tar:
				validSets.append(None)
				continue

			tSet = set()
			for key in uSigs[i]:
				#ret = self.check_intersections(key,sigDicts[i]):
				#if ret != False:
				
				# merge the indexes for corresponding sigs-- this hurts my brain
				#indexlist = []
				#for A in correspondingSigs[i]:
				#	for B in correspondingSigs[i][A]:
				#		indexlist.append(z for z in self.selSigs[B])

				#print("usigs",uSigs) 
				#print("key is", key)
				if self.check_intersections(key,sigDicts[i], correspondingSigs[i][key], i):
					for x in uSigs[i][key]:
						tSet.add(x)

			validSets.append(tSet)

		# Merge all sets:
		out = set(x for x in range(0,len(sigsIn)))
		for i in range(0,len(validSets)):
			if validSets[i] != None:
				out &= validSets[i]
		
		return [sigsIn[x] for x in out]

	def check_intersections(self, mapping, sigDict, CS, sel2):
		# tIndexes is the list of indexes assosciated with the current mapping.
		# tar is the word that we're trimming, sel2 is the position that we're trimming
		# given a mapping (a list of (enc, clr) tuples), and a sigDict
		# Determine if the mapping is valid.  Returns true or false
		# Recall: sigDict[encChar][clrChar] = set of match indexes
		
		sets = []	
		try:		
			for item in mapping:
				sets.append(sigDict[item[0]][item[1]])
		except KeyError:
			# If a key error occurs, the mapping cannot be valid
			return False

		# MAKE A COPY OF THAT SET!!!
		# That took an hour to debug
		x = set(sets[0])
		
		for curr in sets:
			x &= curr
			if len(x) == 0:
				return False

		# Create a set of the clear characters to ignore		
		toRemove = set(mapping[a][1] for a in range(0,len(mapping)))
		tIndexes = []
		
		for A in CS:
			for z in self.selSigs[A]:
				tIndexes.append(z)

		for index in tIndexes:
			Y = set(self.matches[self.tar][index])
			Y -= toRemove

			found = False
			for curr in x:
				X = set(self.matches[sel2][curr])
				X -= toRemove
				
				# Check for intersection of X & Y, if the intersection exists, 
				# then that word is invalid
				if len(X & Y) == 0:
					# FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK
					# GODDAMNMOTHERFUCKING == INSTEAD OF =. FUCK ME.
					found = True
					break

			if found:
				pass
			else:
				self.shitSet.add(index)
		
		return True


def get_sigDicts(encWords,matches):
	# Returns a list containing the sigDicts for each word
	# if an encoded word does not need a sigDict (no shared characters, length of 1)
	# then its position in the list will be None
	# Each sigdict in the list is: sigDict[encChar][clrChar] = set of match indexes

	sigDicts = []
	for i in range(0,len(encWords)):
		if len(encWords[i]) < 2:
			sigDicts.append(None)
			break
		# TODO: Should this threshold be a 1?
		sChars = list(get_shared_chars(encWords,i))
		if len(sChars) < 2:
			sigDicts.append(None)
			break

		sigDicts.append(get_char_sigs(encWords[i],sChars, matches[i]))

	return sigDicts

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

	return sigDict

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