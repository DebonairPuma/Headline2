# This is a list of functions that are no longer in use:

# FROM SETSOLVER.py
def selectWords2Trim(encStr,patDict):
	# This function will try several methods to determine which words are eligible for
	# singleSetTrim/singleSetTrim_thorough.
	# Word stats-> numCharacters, numSharedCharacters, numMatches, 
	# First challenge, eliminate any words that share no characters with other words
	
	maxListLen = 10000

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

# FROM SETSOLVER.py
def singleSetTrim(encWords,matches,sel,threshold):
	# TODO: Automate the process picking sel
	# TODO: Rework this to use the list of all matches, verify that each position matches
	# Attempts to reduce the number of matches for a single word
	# Remember, this is supposed to be a more fault tolerant (and slower) version of set solver
	# The idea is that if we know n words are not in the dictionary, we increase the threshold to n
	# to accomodate them.
	# If all clear words are in the source dictionary, there is NO REASON TO USE THIS!
	# This is a simple (but kind of stupid) method for "ignoring" certain encoded words, in the future
	# it is probably better to just improve set solver so it takes a list of words to ignore

	#print("\tPre trim:",len(matches[sel]))
	start = time.time()
	e2sDicts = [{} for x in range(0,len(encWords))]

	for i in range(0,len(encWords)):
		if i == sel:
			# Don't create one for selected word
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
			if k == sel:
				continue

			sharedChars = set(encWords[k]) & set(encWords[sel])
			# Verify that the set of characters for letter in all contains 
			for char in sharedChars:
				if tmpDict[char] not in e2sDicts[k][char]:
					invalid += 1
					break

		if invalid < threshold:
			trimmedList.append(match)

	stop = time.time()
	#print("\tPost trim:",len(trimmedList))
	#print("\t",trimmedList)
	#print("\tFinished in",stop-start,"seconds\n")

	return trimmedList

# FROM SETSOLVER.py
def checkSolution(encStr, sDict):
	# Attempts to identify when set solver has failed
	# Basically, if the number of unique characters present in
	# sDict is smaller than the number of unique characters in encStr
	# then no solution can exist- returns False in that case

	# TODO: Expand this to work when some sDict entries are being ignored.

	# Get unique chars in encStr:
	uStr = set()
	for char in encStr:
		uStr.add(char)

	# Get unique chars in sDict
	uDict = set()
	for key in sDict:
		uDict |= sDict[key]

	if len(uStr) > len(sDict):
		return False
	else:
		return True