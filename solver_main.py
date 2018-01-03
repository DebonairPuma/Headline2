import time
from copy import *
from setSolver import *
from sigSolver import *
from setupFunctions import *
from grids import cell, GRID

# TODO: Rework the way that the partial status is assigned. It's indistinguishable
# 		from incomplete if we can't produce any chains- so partial should be assigned
# 		only if chains returns something

# TODO: If omit words succeeds, it should probably mark the word that it omitted
# 		that information can be used later when checking the solution

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
		# TODO: Remove partial, it isn't actually used anywhere, hasChains is a better variable
		self.partial = False

		# Set to TRUE when the headline has usable chains
		self.hasChains = False

		# Have we abandoned solving this one by conventional means...
		self.aborted = False

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
		self.getStatus(None)

		# Create a partial Dictionary:
		self.generatepDict(None)
		self.getChains()

		if self.hasChains == True:
			self.nextState = 'E' # Chainable, but could be improved with sigSolve
		elif self.failed == True:
			self.nextState = 'C' # Set Solver with omit words
		elif self.incomplete == True:
			self.nextState = 'B' # SigSolve
		else:
			# Got a partial solution, but no chains, treat as incomplete
			self.nextState = 'B' # SigSolve

	def nextSolve(self):
		# Called by the SOLVER object whenever it runs solveSingles
		if self.nextState == 'B':
			#print("\tIn State B")
			self.sDict = self.sigSolve(self.encWords)
			self.getStatus(None)
			self.generatepDict(None)
			self.getChains()

			if self.hasChains == True:
				self.nextState = 'F' # Chainable, will not benefit from sigSolve
			elif self.failed == True:
				self.nextState = 'D' # Sig solve w/ omit words
			else:
				print("COULD BE SALVAGABLE")
				print([len(self.sDict[key]) for key in self.sDict])
				self.nextState = 'G' # Aborted state
				self.aborted = True
		
		elif self.nextState == 'C':
			#print("\tIn State C")
			self.omitWords(None,True)
			self.getStatus(None)
			self.generatepDict(None)
			self.getChains()	
			
			if self.hasChains == True:
				self.nextState = 'F' # Chainable
			elif self.incomplete == True:
				self.nextState = 'D' # Sig solve w/ omit words
			else:
				#print("Hard Failure")
				self.nextState = 'G' # aborted
				self.aborted = True
		
		elif self.nextState == 'D':
			#print("\tIn State D")
			self.omitWords(None,False)
			self.getStatus(None)
			self.generatepDict(None)
			self.getChains()

			if self.hasChains == True:
				self.nextState = 'F' # Chainable
			else:
				self.nextState = 'G' # aborted
				self.aborted = True

		elif self.nextState == 'E':
			#print("\tIn State E")
			# TODO: add a check here, make sure that sig solve actually improved the results
			self.sDict = self.sigSolve(self.encWords)
			self.getStatus(None)
			self.generatepDict(None)
			self.getChains()

			if self.hasChains == True:
				self.nextState = 'F' # Chainable, sigSolve already run
			else:
				print("Unexpected state! Sig solve made things worse?")
				exit()

		else:
			# We're either in aborted or in chainable.  Either way nothing to do here!
			pass						

	def omitWords(self,clrStr,sFlag):
		# Try using sigSolver but omit a single word at a time until success:
		# This is a painfully simple, yet semi effective method for 
		# handling words that aren't in the dictionary
		# sFlag specifies which solver to use, False = sigSolve, True = setSolve 
		

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
				
				if sFlag == False:
					self.sDict = self.sigSolve(wcopy)
				else:
					tmpMatches = copy(self.allMatches)
					del tmpMatches[i]
					self.sDict = setSolve_slim(wcopy,tmpMatches)
				

				#self.failed = False
				#self.getStatus(None)

				# TODO: Identify incomplete solves
				#if self.failed == False:
				# For now, just keep track of total solutions, and call
				# it a failure if more than one appears
				#potentialSolves +=1
				tpDict = self.generatepDict(self.sDict)

				if len(tpDict.keys()) > len(self.pDict.keys()):
					self.pDict = tpDict
					self.checkSol()
					self.getStatus(None)


					#self.generatepDict(None)


		#if potentialSolves > 1:
		#	#print("HERE!")
		#	self.failed = True
		#	self.partial = False

	def generatepDict(self,dictIn):
		# Converts the current sDict into a pDict
		if dictIn == None:
			dictC = self.sDict
		else:
			dictC = dictIn
	
		curr = {}
		for key in self.sDict:
			try:
				items = list(dictC[key])
				if len(items) == 1:
					curr[key] = items[0]
				else:
					pass
			except:
				print("Got exception in generatepDict...")
				pass

		if dictIn == None:
			self.pDict = curr

		return curr

	def getStatus(self,sDictIn):
		# Evaluates sDict, if all entries map to exactly one letter, then 
		# Solved is set to True
		# If one or more sets has exactly one entry then partialSolved
		# If one or more sets has zero, then failed
		
		if sDictIn == None:
			sDictIn = self.sDict

		# Number of unique characters in string
		uChars = len(self.sDict.keys())

		self.numSolved = 0
		self.numFailed = 0
		
		if self.sDict == None:
			return

		for key in sDictIn:
			if len(sDictIn[key]) == 0:
				self.numFailed += 1
			elif len(sDictIn[key]) == 1:
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

	def sigSolve(self,words):
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
			matches.append(getMatches(words[i],self.patDict))
			#print(words[i],"->",len(matches[i]),"matches")

		# Try an initial shakedown process, basically just running setSovle:
		# this is straight from setSolve
		tsDict  = setSolve_slim(words,matches)
		ret = setTrim(words,tsDict,matches)
		matches = ret[0]


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

		stats = sorted(stats,key=lambda s: s[1])[::-1]

		# Remove any words that are unlikely to be useful:
		fstats = []
		for stat in stats:
			if len(matches[stat[0]]) < maxListLen:
				# Ignore any words that are too short
				if len(words[stat[0]]) > 2:
					if stat[1] > 2:
						fstats.append(stat)


		# After every iteration, try running getSets again:
		for i in range(0,len(fstats)):
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue

			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])			
			matches[fstats[i][0]] = matchList
			tsDict  = setSolve_slim(words,matches)
			ret = setTrim(words,tsDict,matches)
			matches = ret[0]

		
		# TODO: Try a second pass- eventually want to replace this with a loop
		for i in range(0,len(fstats)):
			#print("trying:", words[stats[i][0]])
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue

			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])
			matches[fstats[i][0]] = matchList
			tsDict  = setSolve_slim(words,matches)
			ret = setTrim(words,tsDict,matches)
			matches = ret[0]
		
		for i in range(0,len(matches)):
			print(words[i],len(matches[i]))
		print("#############")
		'''
		for i in range(0,len(fstats)):
			#print("trying:", words[stats[i][0]])
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue

			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])
			matches[fstats[i][0]] = matchList
			tsDict  = setSolve_slim(words,matches)
			ret = setTrim(words,tsDict,matches)
			matches = ret[0]

		for i in range(0,len(fstats)):
			#print("trying:", words[stats[i][0]])
			if len(matches[fstats[i][0]]) > maxListLen:
				# skip any that will take too long
				continue

			ss = SIGSOLVER(words,matches)
			matchList = ss.sigTrim(fstats[i][0])
			matches[fstats[i][0]] = matchList
			tsDict  = setSolve_slim(words,matches)
			ret = setTrim(words,tsDict,matches)
			matches = ret[0]
		'''
		val = getSets(words,matches)
		return val[1]

	def getChains(self):
		# Calls the getChains function with the current pDict
		self.chains = getChains(self.pDict)
		if len(self.chains) > 0:
			self.hasChains = True
		else:
			self.hasChains = False

	def checkSol(self):
		# calls printPartial:
		printPartial(self.pDict,self.encStr,True)

	def tryDict(self,tpDict):
		# Takes a partial dictionary, tDict, and attempts to get a solution 
		# based on that.
		# Omit is a flag that determines whether we try running omit words.
		# TODO: This should also check to see if we have a complete solution...
		# 		could be used to validate everything at the end

		
		# This should check the current status, if it is FAILED, then apply the omit 
		# words approach
		if self.failed:
			# Try omitting words
			# Get a fresh setDict with the knowns from tpDict:
			tsDict = {}
			for key in tpDict:
				if tpDict[key] != '_':
					tsDict[key] = set(tpDict[key])
				else:
					# Don't know, make it general:
					tsDict[key] = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

			# Loop through omitting one at a time:
			words = self.encStr.split(' ')
			while "" in words:
				words.remove("")			

			#potentialSolves = 0
			for i in range(0,len(words)):
				# Ignore any words that are length 1 or 2:
				if len(words[i]) > 2:
					wcopy = list(words)
					del wcopy[i]

					tmatches = deepcopy(self.allMatches)
					del tmatches[i]

					tmpTSdict = deepcopy(tsDict)
					ret = setTrim(wcopy,tmpTSdict,tmatches)
					tmpTSdict = setSolve_slim(wcopy,ret[0])
					self.getStatus(tmpTSdict)

					if self.failed == False:
						#potentialSolves +=1
						pDict = self.generatepDict(tmpTSdict)

						# Check if this solution isi better than the current one:
						if len(pDict.keys()) > len(self.pDict.keys()):
							self.pDict = pDict
							self.sDict = tmpTSdict
					else:
						# Reset status:
						self.getStatus(None)

			# TODO: Make sure this stuff doesn't blow up ^^

		else:
			# Was incomplete, don't omit words:
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

			# compare pDict to current best:		
			pDict = self.generatepDict(tsDict)
			if len(pDict.keys()) > len(self.pDict.keys()):
				self.pDict = pDict
				#printPartial(pDict,self.encStr,True)
				return True

			return False

class SOLVER(object):
	def __init__(self,encStrs,patDict,tree):
		self.start = time.time()
		self.headlines = []
		self.encStrs   = encStrs
		self.patDict   = patDict
		self.tree      = tree
		self.state     = 0
		self.gridSetSize = 0
		self.manual = False
		self.grid = None

		# First, initialize all of the headlines
		for i in range(0,len(encStrs)):
			self.headlines.append(HEADLINE(encStrs[i],patDict,None,i))
		stop = time.time()
		print("Finished initialization in: ", stop-self.start)

		self.main_loop()

	def main_loop(self):
		while True:
			stop = time.time()
			print("Current State: ",self.state,"Elapsed Time: ",stop-self.start)
			print("Status\tSOLVED\tFAILED\tPARTIAL\tINCOMPLETE")
			for headline in self.headlines:
				headline.getStatus(None)
				print(headline.index,"\t",headline.solved,"\t",headline.failed,"\t",headline.partial,"\t",headline.incomplete,"\t")
			print()

			if self.manual == True or self.state > 4:
				break

			self.generateChains()

			if self.gridSetSize == 26:
				done = True
				for headline in self.headlines:
					if headline.solved == False:
						done = False
						break

				if done == True:
					# We've got the longest string and all lines are solved
					break

		print("exited loop:")
		for headline in self.headlines:
			print("LINE:",headline.index)
			printPartial(headline.pDict,headline.encStr,True)
			print()

		if self.grid != None:
			self.grid.printGrid()
		if self.manual == True:
			# For now, this counts as a failure
			return False

		self.getSetting()
		return True

	def generateChains(self):
		self.state  += 1
		self.indexes = []
		self.chains  = []
		for headline in self.headlines:
			headline.getChains()
			if len(headline.chains)<2:
				pass
			else:
				self.indexes.append(headline.index)
				self.chains.append(headline.chains)

		self.startGrid()

	def startGrid(self):
		# Determine which lines have chains:
		tmp    = copy(self.indexes)
		combos = []
		while len(tmp) > 1:
			curr = tmp.pop()
			for index in tmp:
				res = largestSets(self.headlines[curr].chains,
							      self.headlines[index].chains)

				if len(res) == 0:
					continue
				
				# Sort by largest set:
				res = sorted(res,key=lambda s: s[1])[::-1]
				# Store as: ((indexA,indexB),size,seed)		
				combos.append(((curr,index),res[0][1],res[0][0][0]))

		if len(combos) == 0:
			# Cannot make grid, return to single solver techniques
			self.solveSingles()
			return

		# Can now build a grid and attempt to improve it:
		combos = sorted(combos,key=lambda s: s[1])[::-1]

		self.grid = GRID(self.headlines[combos[0][0][0]].chains,
			  			 self.headlines[combos[0][0][1]].chains,
			  			 combos[0][2],
			  			 26,
			  			 13)

		self.gridSetSize = combos[0][1]

		# Mark the lines that are currently being used in the grid
		self.inUse = set([combos[0][0][0],combos[0][0][1]])
		self.improveGrid()

	def improveGrid(self):
		# Try to build a better set using the existing grid:
		bestChains = self.grid.extractChains()
		hChains = bestChains[0]
		vChains = bestChains[1]

		combos = []
		for headline in self.headlines:
			if headline.index not in self.inUse:
				res = largestSets(headline.chains,hChains)
				if len(res) != 0:
					res = sorted(res,key=lambda s: s[1])[::-1]
					combos.append(((headline.index,0),res[0][1],res[0][0][0]))

				res = largestSets(headline.chains,vChains)
				if len(res) != 0:
					res = sorted(res,key=lambda s: s[1])[::-1]
					combos.append(((headline.index,1),res[0][1],res[0][0][0]))

		if len(combos) == 0:
			# Grid is as good as it's going to get.  Try using it!
			self.gridSolve()
			return
			
		combos = sorted(combos,key=lambda s: s[1])[::-1]

		# See if the best combo is better than existing graph:
		if combos[0][1] > self.gridSetSize:
			self.grid = GRID(self.headlines[combos[0][0][0]].chains,
					  		 bestChains[combos[0][0][1]],
					  		 combos[0][2],
					  		 26,
					  		 13)

			self.gridSetSize = combos[0][1]
			self.inUse.add(combos[0][0][0])
			self.improveGrid()
		
		else:
			# Grid is as good as it's going to get.  Try using it!
			self.gridSolve()

	def gridSolve(self):

		for curr in self.headlines:
			ret = self.grid.autoSearch(curr.encWords,curr.uChars,self.tree)
			for sol in ret[1]:
				curr.tryDict(sol)

		# Done with current iteration, returning to main loop

	def solveSingles(self):
		# Order of operations:
		#1st & Failed- try set solve omit words on all
		#1st & incomplete- sig solve on all
		#2nd & failed- sig solve omit words

		# TODO: Experiment with these, should they be run multiple times?

		for headline in self.headlines:
			if headline.solved == True:
				continue

			if self.state == 1:
				if headline.failed == True:
					headline.omitWords(None,True)
				else:
					headline.sDict = headline.sigSolve(headline.encWords)
			elif self.state >= 2:
				if headline.failed == True:
					headline.omitWords(None,False)
				elif headline.incomplete == True: 
					headline.sigSolve(headline.encWords)
		
		if self.state > 4:
			print("Unable to solve enough single lines, switching to manual.\n")
			self.manual = True
		# Done here, returning to main loop
		return

	def getSetting(self):
		print("CONGRATULATIONS! -- This hasn't been added yet")


