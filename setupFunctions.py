from searchTree import *
import time

#################################################################################
# Other Setup Functions
def getPat(word):
	# TODO: Clean this up a bit, it's been a while
	word = word.upper()
	word = word.strip('\n')
	first = len(word)
	last = len(word)
	mapping = {}

	ret = mapWord(word)

	if ret[0] == False:
		return (False,word)
	first = ret[1]

	word = word[::-1]
	mapping = {}
	ret = mapWord(word)
	last = len(word) - ret[1]-1

	word = word[::-1]

	head = word[0:first]
	body = word[first:last+1]
	tail = word[last+1:len(word)]

	mapping = {}

	pat = []
	count = 0

	for i in range(first,last+1):
		if word[i] in mapping:
			pat.append(mapping[word[i]])
		else:
			mapping[word[i]] = count
			pat.append(mapping[word[i]])
			count = count+1

	pat = str(pat)
	return(pat,head,body,tail)

def mapWord(word):
	word = word.upper()
	pos = len(word)
	mapping = {}
	found = False

	for i in range(0,len(word)):
		if word[i] in mapping:
			found = True
			if mapping[word[i]][0]<pos:
				pos = mapping[word[i]][0]
		else:
			mapping[word[i]] = []
			mapping[word[i]].append(i)

	return (found,pos,mapping)

# Return clear to encoded value
def clrMap(clrWord,encWord):
	clrWord = clrWord.upper()
	encWord = encWord.upper()
	mapping = {}
	for i in range(0,len(clrWord)):
		if clrWord[i] in mapping:
			pass
		else:
			mapping[clrWord[i]] = encWord[i]

def buildDict(source,patDict):
	print("Building pattern dictionary from: ",source)
	start = time.time()
	if patDict == None:
		patDict = {}
		patDict["NoPat"] = []

	fp = open(source,"r")

	for line in fp:
		val = getPat(line)

		# if word has pattern
		if val[0] != False:
			if val[0] in patDict:
				patDict[val[0]].append((val[1],val[2],val[3]))
			else:
				patDict[val[0]] = []
				patDict[val[0]].append((val[1],val[2],val[3]))

		# if word has no pattern
		else:
			patDict["NoPat"].append(val[1])

	stop = time.time()
	print("\tFinished in ",stop-start,"seconds")
	return patDict

def getMatches(encWord,patDict):
	# Takes an encoded word and a pattern dictionary
	# Returns a list of potential matches
	matches = []
	pattern = getPat(encWord)

	if pattern[0] == False:
		# Word had no pattern
		l = len(encWord)
		for match in patDict["NoPat"]:
			if len(match) == l:
				matches.append(match)
		return matches
	else:
		# Word has pattern, extract all that have the correct head, body, and tail lengths	
		h = len(pattern[1])
		b = len(pattern[2])
		t = len(pattern[3])
		try:
			for match in patDict[pattern[0]]:
				if len(match[0]) == h and len(match[1]) == b and len(match[2]) == t:
					word = match[0]+match[1]+match[2]
					matches.append(word)
		except KeyError:
			pass
			#print("This word",encWord,"has no pattern. Good luck with that!")
			
	return matches

def updatePartial(key,val,Dict):
	# for ecn->clr, use key as enc
	# for clr->enc, use key as clr
	pDict = dict(Dict)
	key = key.upper()
	val = val.upper()
	for i in range(0,len(key)):
		if key[i] in pDict:
			pass
		else:
			# Ignore Placeholders
			if val[i] != '_':
				pDict[key[i]] = val[i]
	return pDict

def printPartial(pDict,line,pFlag):
	#print(pDict)
	newLine = ""
	for i in range(0,len(line)):
		if line[i] in pDict:
			newLine = newLine + pDict[line[i]]
		else:
			newLine = newLine + " "
	if pFlag == True:
		print(newLine)
		print(line)
	return newLine

def getChains(pDict):
	# Takes a partial dictionary and returns a list of chains
	
	e2cDict = pDict
	# Reverse pDict so we have a c2eDict:
	c2eDict = {}
	for key in pDict:
		c2eDict[pDict[key]] = key

	uChars = set()	# Keep track of used characters
	chains = []

	for key in e2cDict:
		# Pass on characters we've already done	
		if key in uChars:
			continue
		failed = False
		tstr = key
		uChars.add(tstr[-1])

		while tstr[-1] in e2cDict:
			tstr += e2cDict[tstr[-1]]
			uChars.add(tstr[-1])
			if len(tstr) >26:
				failed = True
				break

		# Search in the opposite direction:
		while tstr[0] in c2eDict:
			tstr = c2eDict[tstr[0]] + tstr
			uChars.add(tstr[0])
			if len(tstr) >26:
				failed = True
				break
	
		if not failed:
			chains.append(tstr)

	return chains

def largestSets(listA,listB):
	# Takes two lists of chains, A and B
	# First, determine which items in A and B are linked
	# Then connects them all and determines the size of the linked set
	# Returns a list with an identifier for each distinct set and it's size
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

def getSetting(fullStr,clrStrings,encStrings,tree):
	# TODO: Set this up with a manual flag.  If we weren't able to find a valid setting, allow the user to look at it
	#		If no valid words are found, we're going to just try getKey on all possible shifts
	# Takes full encoded alphabet and clear/encoded strings
	# attempts to determine the 5 letter setting

	print("\n\tSearching for Setting...\n")

	settings = []
	dicts = []
	# Create list of partial dictionaries
	for i in range(0,len(clrStrings)):
		# TODO: Try to make this a single line
		tDict = {}
		tDict = updatePartial(clrStrings[i],encStrings[i],tDict)
		dicts.append(tDict)

	# holds rotated partial strings
	rotatedStrs = [""]*len(dicts)

	# Create partial strings in the correct position with ' ' placeholders
	for i in range(0,len(dicts)):
		for j in range(0,25):
			if fullStr[j] in dicts[i]:
				rotatedStrs[i] = rotatedStrs[i] +dicts[i][fullStr[j]]
			else:
				rotatedStrs[i] = rotatedStrs[i] + " "

	# Fill in the spaces with info from the full string
	for i in range(0,len(dicts)):
		found = False
		for j in range(0,25):
			if rotatedStrs[i][j] != " ":
				for k in range(0,25):
					if fullStr[k] == rotatedStrs[i][j]:
						settings.append(fullStr[k-j:] + fullStr[0:k-j])
						found = True
						break

			if found == True:
				break
		if found == False:
			print("WARNING: Problem finding rotated string, longest string might have repeats!")
			settings.append(fullStr)

	# Search for words in the recover matrix
	possibleSettings = []
	for i in range(0,len(fullStr)):
		word = ""
		for j in range(0,len(settings)):
			word += settings[i][j]

		# Test the word backwards and forwards, append it if it works
		if findFull(tree,word) == True:
			possibleSettings.append((i,word))
		if findFull(tree,word[::-1]) == True:
			possibleSettings.append((i,word[::-1]))

	# If only one word was found, skip manual entry portion:
	if len(possibleSettings) == 1:
		skip = True
	else:
		skip = False

	if skip == False:
		# Manually select the correct word to get shift
		print("\tFound these words:")
		for i in range(0,len(possibleSettings)):
			print("\t",i,"-->",possibleSettings[i][1])
		print ("\n")

		try:
			sel = int(str(input("\tEnter selection number or char to try manual\n")),10)
			# REMEMBER: This is a tuple! You're setting shift to the right value
			shift = possibleSettings[sel][0]
		except:
			sel = None

		if sel == None:
			# Manually getting setting
			print(fullStr,"\n")
			tStr = " --> A B C D E F G H I J K L M N O P Q R S T U V W X Y Z\n"
			print(tStr)

			for i in range(0,len(settings)):
				tStr = ""
				for j in range(0,len(settings[i])):
					tStr = tStr + settings[i][j] + " "
				tStr = tStr.upper()
				print(i,"-->",tStr)
			tar = str(input("\nSelect Offset Letter\n"))
			
			# Yeah there's probably a cleaner way to do this
			alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
			shift = alpha.find(tar)

	else:
		# Full auto, get shift
		print("\n\tUsing only found word...")
		shift = possibleSettings[0][0]

	# Shift everything full to left
	fullStr = fullStr[shift:] + fullStr[:shift]
	for i in range(0,len(settings)):
		settings[i] = settings[i][shift:] + settings[i][:shift]

	setting = ""
	for i in range(0,len(settings)):
		setting = setting +settings[i][0]

	print("\t\tSetting is:",setting,"\n")
	return (fullStr,setting)


