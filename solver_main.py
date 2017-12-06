from setSolver import *
from sigSolver import *
from setupFunctions import *


class HEADLINE(object):
	# An object for storing an encoded headline and some relevant data about it
	# Stats: Number of unique letters
	# Letters by frequency
 
	def __init__(self,encStr,patDict,pDict,index):
		# Initialize status variables:
		self.index = index # Keeps track of which line this one is.
		# sDict contains exactly one character for every character in it
		self.solved = False

		# sDict contains some fully solved characters, and no empty sets
		self.partial = False

		# sDict contains one or more empty sets (probably all empty sets)
		# Usually means the encoded string contains an unknown word. omitWords
		# may be able to find a solution.
		self.failed = False

		# sDict contains too many extraneous characters, solution may
		# not be possible via sigSolve or setSolve
		self.incomplete = False

		# encStr is the headline we wish to solve
		# pDict contains any mappings we've already confirmed.
		self.patDict = patDict
		self.encStr = encStr
		self.encWords = encStr.split(" ")
		while "" in self.encWords:
			self.encWords.remove("")

		self.uChars = set(encStr)
		self.uChars.discard(' ')

		self.allMatches = []
		for i in range(0,len(self.encWords)):
			self.allMatches.append(getMatches(self.encWords[i],self.patDict))

		# Run Set Solve
		self.sDict = setSolve(self.encStr,self.patDict)

		# Evaluate sDict and set status accordingly
		self.getStatus()


		# TODO: Evaluate how often this is actually helpful, in most we can probably
		# 		skip this step until everything has been initialized.
		if self.failed ==False and self.solved == False:
			# If failed, implies we have an unknown word
			# If not solved, implies sigSolve may yet be effective
			words = self.encStr.split(' ')
			while "" in words:
				words.remove("")

			self.sDict = self.sigSolve(words, self.patDict)
			self.getStatus()

		# Create a partial Dictionary:
		self.generatepDict()

	def omitWords(self,clrStr):
		# Try using sigSolver but omit a single word at a time until success:
		# This is a painfully simple, yet semi effective method for 
		# handling words that aren't in the dictionary
		# TODO: add a flag to specify which version of 
		# omit words we want to run sigSolve, or setSolve.
		

		# TODO: This can generate more than one solution.  We need to detect when that
		# 		happens and account for it somehow.  Determine which solution is the 
		# 		best, or which combination is the best
		# How many potential solutions do we have?
		potentialSolves = 0


		words = self.encStr.split(' ')
		while "" in words:
			words.remove("")

		for i in range(0,len(words)):
			# Ignore any words that are length 1 or 2:
			if len(words[i]) > 2:
				wcopy = list(words)
				del wcopy[i]
				
				self.sDict = self.sigSolve(wcopy,self.patDict)
				#self.sDict = self.sigSolve(wcopy,self.patDict)
				

				self.failed = False
				self.getStatus()

				# TODO: Identify incomplete solves
				if self.failed == False:
					# For now, just keep track of total solutions, and call
					# it a failure if more than one appears
					potentialSolves +=1
					self.generatepDict()
					#print("Omitted: ",words[i])
					#printPartial(self.pDict,self.encStr,True)
					#if clrStr != None:
					#	print(clrStr)
					#print()

		if potentialSolves > 1:
			self.failed = True
			self.partial = False

	def generatepDict(self):
		# Converts the current sDict into a pDict
		self.pDict = {}
		for key in self.sDict:
			try:
				items = list(self.sDict[key])
				if len(items) == 1:
					self.pDict[key] = items[0]
				else:
					pass
			except TypeError:
				pass

	def getStatus(self):
		# Evaluates sDict, if all entries map to exactly one letter, then 
		# Solved is set to True
		# If one or more sets has exactly one entry then partialSolved
		# If one or more sets has zero, then failed
		
		# Number of unique characters in string
		uChars = len(self.sDict.keys())

		self.numSolved = 0
		self.numFailed = 0
		
		if self.sDict == None:
			return

		for key in self.sDict:
			if len(self.sDict[key]) == 0:
				self.numFailed += 1
			elif len(self.sDict[key]) == 1:
				self.numSolved += 1

		# Reset variables:
		self.solved = False
		self.partial = False
		self.failed = False
		self.incomplete = False

		if self.numFailed > 0:
			self.failed = True
		elif self.numSolved >= 0:
			self.partial = True
			if self.numSolved == uChars:
				self.solved = True
		else:
			self.incomplete = True

	def sigSolve(self,words,patDict):
		# This function will try several methods to determine which words are eligible for
		# singleSetTrim/singleSetTrim_thorough.
		# Word stats-> numCharacters, numSharedCharacters, numMatches, 
		# First challenge, eliminate any words that share no characters with other words
		
		# TODO: Cleanup!

		maxListLen = 10000

		#print(encStr)
		#start = time.time()


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
			#matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])
				
			matches[fstats[i][0]] = matchList
			matches = setSolve_slim(words,matches)


		# Try a second pass- eventually want to replace this with a loop
		for i in range(0,len(fstats)):
			#print("trying:", words[stats[i][0]])
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue
			#matchList = singleSetTrim_thorough(words,matches,fstats[i][0],1)
			#matchList = singleSetTrim(words,matches,fstats[i][0],1)
			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])

			matches[fstats[i][0]] = matchList
			matches = setSolve_slim(words,matches)

		val = getSets(words,matches)
		return val[1]

	def getChains(self):
		# Calls the getChains function with the current pDict
		self.chains = getChains(self.pDict)

	def checkSol(self):
		# calls printPartial:
		printPartial(self.pDict,self.encStr,True)

	def tryDict(self,tpDict,omit):
		# Takes a partial dictionary, tDict, and attempts to get a solution 
		# based on that.
		# Omit is a flag that determines whether we try running omit words.
		# TODO: This should also check to see if we have a complete solution...
		# 		could be used to validate everything at the end

		if omit == False:
			# Get a fresh setDict with the knowns from tpDict:
			tsDict = {}
			for key in tpDict:
				if tpDict[key] != '_':
					tsDict[key] = set(tpDict[key])
				else:
					# Don't know, make it general:
					tsDict[key] = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

			tmatches = copy(self.allMatches)
			ret = setTrim(self.encWords,tsDict,tmatches)

			tmatches = ret[0]
			count = ret[1]
			#tmatches = ret[0]			
			while count != 0:
				val = getSets(self.encWords,tmatches)
				ret = setTrim(self.encWords,val[1],tmatches)
				matches = ret[0]
				count = ret[1]

			# Check for failures:
			tsDict = val[1]
			for key in tsDict:
				if len(tsDict[key]) == 0:
					# Failed
					return False

			# if no failures, return the sDict:
			# This is literally just getpDict() # TODO: Remove this
			pDict = {}
			for key in tsDict:
				try:
					items = list(tsDict[key])
					if len(items) == 1:
						pDict[key] = items[0]
					else:
						pass
				except TypeError:
					pass	
			printPartial(pDict,self.encStr,True)

			

		else:
			pass

