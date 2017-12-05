from setupFunctions import updatePartial

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
	def __init__(self,size,vChain,hChain,seedPos,seed):
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
		self.seedGrid(seedPos,seed)
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

	def seedGrid(self,pos,char):
		self.grid[pos][pos].fill(char)

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

	def findLongest(self):
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

	def autoSearch(self,encHeadline,tree):
		# TODO: Refine this process.  Need to dramatically improve the filtering of bogus strings and remove user interaction
		#		If nothing else, eliminate the need for user to select initial char
		# same as offset dict, but automatically searches the grid for every possible pair

		# TODO: Reorder this in terms of most likely to be used chars:
		alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		# if more than half the words are invalid reject it
		encWords = encHeadline.split(" ")
		TOLERANCE = len(encWords)/2

		pairs = []
		strs = []

		sel = str(input("Select encoded letter to try:\n")).upper()
		for clr in alpha:
			(offX,offY) = self.autoFindOffset(sel,clr)
			if offX == 0 and offY == 0:
				# Didn't find a match, move on
				continue

			# Assemble tencoded string with offset
			clrStr = ""
			pDict = {}
			for key in encHeadline:
				if key == " ":
					clrStr = clrStr + " "
				elif key in pDict:
					clrSTr = clrStr +pDict[key]
				else:
					newVal = self.searchGrid(key,offX,offY)
					if newVal != None:
						pDict[key] = newValclrStr = clrStr+pDict[key]
					else:
						clrStr = clrStr +"_"

			# Split encoded string up into searchable words
			invalid = 0
			clrWords = clrStr.split(" ")

			# TODO: Make this work with wildcards
			for word in clrWords:
				# if word is complete, no underscores
				if word.find('_') == -1:
					if findWord(tree,word) == False:
						invalid += 1
					if invalid >= TOLERANCE:
						break

				if invalid < TOLERANCE:
					pairs.append((sel,clr))
					strs.append(clrStr)

			for i in range(0,len(pairs)):
				print(i,":", pairs[i][0],"->",pairs[i][1],"\at",strs[i])

			try:
				if len(pairs) != 0:
					sel = int(str(raw_input("Select Match to return or Q to quit without saving\n")))
					pDict = {}
					clrWrds = strs[sel].split(" ")
					for i in range(0,len(encWords)):
						pDict = updatePartial(encWords[i],clrWrds[i],pDict)
					return pDict
				else:
					# TODO: Has this ever happened??
					print("No valid strings found")
					return None
			except:
				return None
				
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

		print("No match found!\n")
		return(0,0)