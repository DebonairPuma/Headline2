def signature_main(words, matches, sel, patDict):
	#print(matches[sel][5])

	# Get the list of significant characters for selected word:
	selSchars = list(get_shared_chars(words, sel))

	#print("selSchars")
	#print(selSchars)

	# Get the dict of signatures for the selected word
	# selSIgs: Keys="clrSig", Values=[matches with that clrSig]
	selSigs = get_sig_sel(words[sel],selSchars, matches[sel])

	#print("selSigs")
	#print(selSigs)

	# Get the character dictionaries for each other word
	# charDicts[0]->charDict[encChar][clrChar] = set of match indexes
	charDicts = get_all_sigDicts(words,matches)

	#print("charDicts")
	#print(charDicts)

	# Run find valid signatures:
	ret = find_valid_signatures(selSchars, selSigs.keys(), charDicts)

	# Trim these based on "irrelevant" mappings


	# Ret is a list of valid signatures, combine the ones that are OK
	# and then fetch the valid matches
	vindexes = []
	out = []

	for vsig in ret:
		for index in selSigs[vsig]:
			out.append(matches[sel][index])

	return out

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

def get_all_sigDicts(encWords,matches):
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

def check_intersections(mapping, sigDict, matches, tIndexes, sel, sel2):
	# tIndexes is the list of indexes assosciated with the current mapping.
	# sel is the word that we're trimming
	# given a mapping (a list of (enc, clr) tuples), and a sigDict
	# Determine if the mapping is valid.  Returns true or false
	# Recall: sigDict[encChar][clrChar] = set of match indexes
	#print("\t\tin intersections")
	#for key in sigDict:
	#	print(key,sigDict[key].keys())
	#	print()
	sets = []	
	try:
		
		for item in mapping:
			sets.append(sigDict[item[0]][item[1]])
		#print("\t\tno key error")
	except KeyError:
		# If a key error occurs, the mapping cannot be valid
		#print("\t\tkey error")
		return False

	# MAKE A COPY OF THAT SET!!!
	# That took an hour to debug
	x = set(sets[0])
	
	for curr in sets:
		#print("Curr set:",curr)
		x &= curr
		if len(x) == 0:
			return False

	# Create a set of the clear characters to ignore
	toRemove = set(mapping[a][1] for a in range(0,len(mapping)))

	outIndexes = []
	for index in tIndexes:
		Y = set(matches[sel][index])
		Y -= toRemove

		found = False
		for curr in x:
			X = set(matches[sel2][curr])
			X -= toRemove

			# Check for intersection of X & Y, if the intersection exists, 
			# then that word is invalid
			if len(X & Y) == 0:
				found == True
				break

		if found:
			outIndexes.append(index) 

	return outIndexes

		# Iterate through items of X and find if any are valid


	'''
	# Check on the clear mappings
	
	# For every match (in Y) associated with the current signature, create a set of the clear
	# characters that all non shared characters map to
	#	Now, for all matches in set X, create a set of all the clear characters that all non
	#	shared characters map to
	#	If these sets intersect, then remove the index from X.  If X is empty, proceed to 
	#	the next match in Y.  If after this loop, X contains at least 1 item, append it

	'''

def get_sig_tuples(encSig, clrSig, tChars):
	# Just creates a list of (encChar,clrChar) tuples
	#out = [(encSig[i],clrSig[i]) for i in range(0,len(encSig))]
	#return out
	# Slightly more useable version, only creates tuples for shared chars
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

def find_valid_signatures(eSchars, sigsIn, sigDicts):
	# TODO: Once it's easier to understand, try optimizing it.
	# eSchars is a list of encoded shared characters from the target word
	# Checks to see which signatures (if any) are valid
	
	validSigs = []
	setOftChars = set(eSchars)

	sigsIn = list(sigsIn)
	# For every signature, establish a set of subsignatures that we need to apply 
	# to each word:
	# LIST [ DICTS ], where keys are sigTuples, and values are indexes of sigsIn that use
	# That signature


	uSigs = []
	for i in range(0,len(sigDicts)):
		if sigDicts[i] == None:
			uSigs.append(None)
			continue

		# Get the set of shared characters for this word:
		sEncChars = set(sigDicts[i].keys())
		sEncChars = sEncChars & setOftChars			

		tDict = {}
		for j in range(0,len(sigsIn)):
			iTuple = tuple(get_sig_tuples(eSchars,sigsIn[j], sEncChars))
			if iTuple in tDict:
				# We've already seen this tuple set
				tDict[iTuple].append(j)
			else:
				# We haven't seen this tuple yet, establish a new list:
				tDict[iTuple] = [j]
		uSigs.append(tDict)
	
	# Run check intersections on all:
	validSets = []
	for i in range(0,len(sigDicts)):
		if uSigs[i] == None:
			validSets.append(None)
			continue

		tSet = set()
		for key in uSigs[i]:
			ret = check_intersections(key,sigDicts[i]):
			if ret != False:
				

			#if check_intersections(key,sigDicts[i]):
			#	for x in uSigs[i][key]:
			#		tSet.add(x)

		validSets.append(tSet)

	# Merge all sets:
	out = set(x for x in range(0,len(sigsIn)))
	for i in range(0,len(validSets)):
		if validSets[i] != None:
			out &= validSets[i]
	
	return [sigsIn[x] for x in out]





