from setupFunctions import getMatches
import time

def setSolve(encStr,patDict):
	# Takes an encoded string and attempts to solve it:
	words = encStr.split(' ')
	while "" in words:
		words.remove("")
	matches = []
	for i in range(0,len(words)):
		matches.append(getMatches(words[i],patDict))

	val = getSets(words,matches)
	ret = setTrim(words,val[1],matches)
	matches = ret[0]
	count = ret[1]

	while count != 0:
		val = getSets(words,matches)
		ret = setTrim(words,val[1],matches)
		matches = ret[0]
		count = ret[1]

	# returns sDcit from the most recent run
	return val[1]

def setSolve_slim(words,matches):
	# Simplified setSolve, returns matches rather than sets
	val = getSets(words,matches)
	ret = setTrim(words,val[1],matches)
	matches = ret[0]
	count = ret[1]

	while count != 0:
		val = getSets(words,matches)
		ret = setTrim(words,val[1],matches)
		matches = ret[0]
		count = ret[1]	

	return val[1]

def getSets(encWords,matches):
	# Given a set of encoded words and their possible matches, gets sets of possible characters
	# for each position in each word
	# also returns the smallest shared set for each encoded character in the form of a dict

	sets = []
	for i in range(0,len(encWords)):
		# Create empty sets
		sets.append([set() for x in range(0,len(encWords[i]))])
		for j in range(0,len(matches[i])):
			for k in range(0,len(encWords[i])):
				sets[i][k].add(matches[i][j][k])

	sDict = {}
	for i in range(0,len(encWords)):
		for j in range(0,len(encWords[i])):
			if encWords[i][j] in sDict:
				# Append next set if an entry already exists
				sDict[encWords[i][j]].append(sets[i][j])
			else:
				sDict[encWords[i][j]] = []
				sDict[encWords[i][j]].append(sets[i][j])

	# Now iterate through each key in sDict and find the shared set for each character
	for key in sDict:
		# Establish an initial set
		tmp = sDict[key][0]
		# Get the intersection of all sets
		for curr in sDict[key]:
			tmp = tmp & curr
		# Place the intersection set back in sDict
		sDict[key] = tmp

	# Finally, run remove singles
	sDict = removeSingles(sDict)

	return (sets,sDict)

def setTrim(words,sDict,matches):
	# Given sDict (dict of possible sets) a list of encoded words, and a list of matches
	# removes any matches that violate the existing sets:

	# Also returns the number of entries removed
	count = 0
	# Iterate through all encoded words
	for i in range(0,len(matches)):
		# Iterate through all matches for each
		tmpMatches = []
		for j in range(0,len(matches[i])):
			valid = True
			for k in range(0,len(words[i])):
				if matches[i][j][k] in sDict[words[i][k]]:
					pass
				else:
					valid = False
					count += 1
					break

			if valid == True:
				tmpMatches.append(matches[i][j])
		matches[i] = tmpMatches

	return (matches,count)

def removeSingles(sDict):
	# Takes an sDict and finds any sets with only one character
	# Then removes that character from all other sets
	# Repeats until no characters are removed

	count = None
	while count != 0:
		count = 0
		for key in sDict:
			if len(sDict[key]) == 1:
				char = sDict[key].pop()

				for s in sDict:
					try:
						sDict[s].remove(char)
						count +=1
					except KeyError:
						pass
				# Add the char back into position
				sDict[key].add(char)

	return sDict

# TODO: This can be removed, it still somehow trims more than sigSolver, but I don't
# 		know why.  sigSolver is fast enough though that it's always the better choice
def singleSetTrim_thorough(encWords,matches,sel,threshold):
	# Attempts to reduce the number of matches for a single word
	# Similar in spirit to singleSetTrim, but this iterates through all possible matches for each
	# This seems to be about ten times slower than the other version, though it does consistently yield better results

	e2sDicts = [{} for x in range(0,len(encWords))]
	# This is useful only for words that have only one letter in common with sel
	for i in range(0,len(encWords)):
		if i == sel:
			# Don't create one for selected word
			continue
		if len(encWords[i]) < 3:
			continue

		# Initialize Sets (one set for every unique encoded character)
		for char in encWords[i]:
			if char not in e2sDicts[i]:
				e2sDicts[i][char] = set()

		# Populate Sets
		for match in matches[i]:
			for j in range(0,len(match)):
				e2sDicts[i][encWords[i][j]].add(match[j])


	# Set up tmpDict- will be used to hold the letter:value pairs for each potential word
	tmpDict = {x:"_" for x in encWords[sel]}
	trimmedList = []

	
	# Try all matches in the list:
	for match in matches[sel]:
		invalid = 0 # Number of words that have been invalidated
		# Reset tmpDict
		for i in range(0,len(encWords[sel])):
			tmpDict[encWords[sel][i]] = match[i]

		# See which, if any, words are incompatible with this solution:
		for k in range(0,len(encWords)):
			# Skip itself
			if k == sel:
				continue
			# Also skip any words that are of length 2 or less
			if len(encWords[k]) < 3:
				continue


			sharedChars = set(encWords[k]) & set(encWords[sel])
			if len(sharedChars) == 1:
				# Verify that the set of characters for letter in all contains 
				# This is the quick method
				for char in sharedChars:
					if tmpDict[char] not in e2sDicts[k][char]:
						invalid += 1
						break
			elif len(sharedChars) > 1:
				# Longer method, iterate through all potential matches for this position
				# the match from matches[sel] is invalid if it removes all options from the list of matches
				# for a particular position, so we only need to iterate through here until we find a word that
				# is actually valid
				found = False
				tstDict = {x:"_" for x in encWords[k]}
				for word in matches[k]:
					for z in range(0,len(encWords[k])):
						tstDict[encWords[k][z]] = word[z]

					exit = False
					for shared in sharedChars:
						if tstDict[shared] != tmpDict[shared]:
							exit = True
							break
					
					if exit == False:
						found = True
						break
				
				if found == False:
					invalid +=1


		if invalid < threshold:
			trimmedList.append(match)

	return trimmedList
