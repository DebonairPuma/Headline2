from setupFunctions import updatePartial
from searchTree import searchWildTF

class cell(object):
	def __init__(self):
		self.char = None
		self.done = False
		self.hasChar = False
	def fill(self,newChar):
		self.hasChar = True
		self.char = newChar
	def mark(self):
		self.done = True

class GRID(object):
	def __init__(self,vChain,hChain,seed,size,seedPos):
		# If no seed specifided we're running in manual mode and should pick one

		if seed == None:
			print("vChains:",vChain)
			print("hChains:",hChain)
			seed = str(input("\nPickSeed\n")).upper()

		self.size = size
		self.grid = [[cell() for x in range(0,self.size)] for y in range(0,self.size)]
		self.vChain = vChain
		self.hChain = hChain

		self.uD = {}
		self.dD = {}
		self.lD = {}
		self.rD = {}
		self.ingestChains()

		self.changes = None
		# Seed the grid:
		self.grid[seedPos][seedPos].fill(seed)
		self.growGrid()

	def ingestChains(self):
		# hor chains left to right
		for chain in self.hChain:
			for i in range(0,len(chain)-1):
				self.rD[chain[i]] = chain[i+1]

		# reverse chain to read right to left
		for chain in self.hChain:
			chain = chain[::-1]
			for i in range(0,len(chain)-1):
				self.lD[chain[i]] = chain[i+1]

		# ver chains top to bottom
		for chain in self.vChain:
			for i in range(0,len(chain)-1):
				self.dD[chain[i]] = chain[i+1]

		# reverse chain to read bottom to top
		for chain in self.vChain:
			chain = chain[::-1]
			for i in range(0,len(chain)-1):
				self.uD[chain[i]] = chain[i+1]

	def growGrid(self):
		while self.changes != 0:
			self.changes = 0
			for x in range(0,self.size):
				for y in range(0,self.size):
					# cell has character, but neighbors haven't been filled
					self.tryFill(x,y)

	def tryFill(self,x,y):
		if (self.grid[x][y].hasChar == True) and (self.grid[x][y].done == False):
			# Mark cell so we don't repeat it
			self.grid[x][y].mark()
			# TODO: Can probably remove try except structure:
			# Try to fill up:
			try:
				if y !=0:
					if (self.grid[x][y-1].hasChar == False):
						if (self.grid[x][y].char in self.uD):
							self.grid[x][y-1].fill(self.uD[self.grid[x][y].char])
							self.changes += 1
			except IndexError:
				pass

			# Try to fill down:
			try:
				if y !=self.size:
					if (self.grid[x][y+1].hasChar == False):
						if (self.grid[x][y].char in self.dD):
							self.grid[x][y+1].fill(self.dD[self.grid[x][y].char])
							self.changes += 1
			except IndexError:
				pass

			# Try to fill left:
			try:
				if x !=0:
					if (self.grid[x-1][y].hasChar == False):
						if (self.grid[x][y].char in self.lD):
							self.grid[x-1][y].fill(self.lD[self.grid[x][y].char])
							self.changes += 1
			except IndexError:
				pass
			
			# Try to fill right:
			try:
				if x !=self.size:
					if (self.grid[x+1][y].hasChar == False):
						if (self.grid[x][y].char in self.rD):
							self.grid[x+1][y].fill(self.rD[self.grid[x][y].char])
							self.changes += 1
			except IndexError:
				pass

	def printGrid(self):
		xStr = ""
		for y in range(0,self.size):
			xStr = ""
			for x in range(0,self.size):
				if self.grid[x][y].char != None:
					xStr = xStr + self.grid[x][y].char
				else:
					xStr = xStr + " "
			print(y,":\t",xStr)
		print("\n")

	def extractChains(self):
		# TODO: This can be slimmed down considerably, not any faster, just
		# 		easier to look at
		# Returns a list of the longest chains in the X & Y directions
		hDict = {}
		for y in range(0,self.size):
			for x in range(0,self.size):
				if self.grid[x][y].char != None:
					if self.grid[x][y].char not in hDict:
						try:
							if self.grid[x+1][y].char != None:
								hDict[self.grid[x][y].char] = self.grid[x+1][y].char
						except:
							pass

		vDict = {}
		for x in range(0,self.size):
			for y in range(0,self.size):
				if self.grid[x][y].char != None:
					if self.grid[x][y].char not in vDict:
						try:
							if self.grid[x][y+1].char != None:
								vDict[self.grid[x][y].char] = self.grid[x][y+1].char
						except:
							pass

		hrDict = {}
		for key in hDict:
			hrDict[hDict[key]] = key

		vrDict = {}
		for key in vDict:
			vrDict[vDict[key]] = key

		huChars = set()
		vuChars = set()
		hChains = []
		vChains = []
		for key in hDict:
			# Pass on characters we've already done	
			if key in huChars:
				continue
			failed = False
			tstr = key
			huChars.add(tstr[-1])

			while tstr[-1] in hDict and hDict[tstr[-1]] not in tstr:
				tstr += hDict[tstr[-1]]
				huChars.add(tstr[-1])
				if len(tstr) >26:
					failed = True
					break

			# Search in the opposite direction:
			while tstr[0] in hrDict and hrDict[tstr[-1]] not in tstr:
				tstr = hrDict[tstr[0]] + tstr
				huChars.add(tstr[0])
				if len(tstr) >26:
					failed = True
					break
		
			if not failed:
				hChains.append(tstr)

		for key in vDict:
			# Pass on characters we've already done	
			if key in vuChars:
				continue
			failed = False
			tstr = key
			vuChars.add(tstr[-1])

			while tstr[-1] in vDict and vDict[tstr[-1]] not in tstr:
				tstr += vDict[tstr[-1]]
				vuChars.add(tstr[-1])
				if len(tstr) >26:
					break

			# Search in the opposite direction:
			while tstr[0] in vrDict and vrDict[tstr[-1]] not in tstr:
				tstr = vrDict[tstr[0]] + tstr
				vuChars.add(tstr[0])
				if len(tstr) >26:
					break
		
			if not failed:
				vChains.append(tstr)

		return(hChains,vChains)

	def autoSearch(self,words,uChars,tree):
		# Attempts to solve a headline using the grid
		# Words is a list of encoded words
		# uChars is the list of unique characters from those words
		# tree is the search tree
		
		alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		
		# How many invalid words a line can have before being rejected
		TOLERANCE = 1

		pairs = []	# Pairs of letters that worked
		dicts = []	# The dictionaries for those

		# Grab an arbitrary character
		# TODO: Is this OK?
		tar = words[0][0]

		for clr in alpha:
			(offX,offY) = self.autoFindOffset(tar,clr)
			if offX == 0 and offY == 0:
				# Didn't find a match, move on
				continue

			# Create a pDict using that offset:
			pDict = {}
			for char in uChars:
				val = self.searchGrid(char,offX,offY)
				if val == None:
					pDict[char] = '_'
				else:
					pDict[char] = val

			# Decode each encoded word using pDict and search for it in tree
			invalid = 0

			for word in words:
				tclr = ""
				for char in word:
					tclr += pDict[char]

				# Seach the tree
				# TODO: Using wildcard search may not be worth it here:
				if searchWildTF(tclr,tree) == False:
					invalid += 1

			if invalid < TOLERANCE:
				pairs.append((tar,clr))	
				dicts.append(pDict)			

		return (pairs,dicts)
				
	def autoFindOffset(self,enc,clr):
		# Finds enc and clr, then returns the X & Y offsets
		xOff = None
		yOff = None
		done = False

		for x in range(0,self.size):
			for y in range(0,self.size):
				if done == True:
					return(xOff,yOff)
				if (self.grid[x][y].char == enc):
					# Start searching down/right
					for x2 in range(0,self.size):
						if done == True:
							break
						for y2 in range(0,self.size):
							if (self.grid[x2][y2].char == clr):
								# Found a match
								xOff = x2-x
								yOff = y2-y
								if ((xOff == 1) or (xOff == 0) or (xOff == -1)):
									pass
								else:
									done = True
									break

		#print("No match found!\n")
		return(0,0)

	def searchGrid(self,char,offX,offY):
		# returns the character located at that offset
		val = None
		for x in range(0,self.size):
			for y in range(0,self.size):
				if (self.grid[x][y].char == char):
					try:
						val = self.grid[x+offX][y+offY].char
						return val
					except:
						pass

	def findLongest(self):
		# TODO: This function can probably be removed, extract chains is better
		longX = ""
		longY = ""

		for x in range(0,self.size):
			ty = ""
			for y in range(0,self.size):
				if self.grid[x][y].char == None:
					ty = ""
				else:
					ty = ty +self.grid[x][y].char
				if len(ty) > len(longY):
					longY = ty

		for y in range(0,self.size):
			tx = ""
			for x in range(0,self.size):
				if self.grid[x][y].char == None:
					tx = ""
				else:
					tx = tx +self.grid[x][y].char
				if len(tx) > len(longX):
					longX = tx

		print("longest strings:")
		print("x:",longX)
		print("y:",longY)
		print("\n")

		xset = set()
		yset = set()
		for char in longX:
			xset.add(char)
		for char in longY:
			yset.add(char)

		if len(yset) > len(xset):
			return longY
		else:
			return longX 
