# Search Tree
import time

class NODE(object):
	def __init__(self,char,parent):
		self.char = char
		self.parent = parent
		self.children = []
		self.isEnd = False

def buildTree(source,tree):
	# given a file descriptor, builds a search tree
	# returns a handle for the tree object
	print("Building search tree from: ",source)
	start = time.time()
	
	if tree == None:
		tree = NODE(None,None)

	fp = open(source,"r")
	for word in fp:
		word = word.upper()
		word = word.strip('\n')
		curr = tree
		for char in word:
			found = False
			for child in curr.children:
				# Search Children for existing node
				if child.char == char:
					# If found, move to that node and continue
					curr = child
					found = True
					break
			
			if found == False:
				# Didn't find the character, add a new node and continue
				nxt = NODE(char,curr)
				curr.children.append(nxt)
				curr = nxt
		# Mark the node as the end of a word
		curr.isEnd = True	

	stop = time.time()
	print("\tFinished in: ",stop-start,"seconds")
	return tree

def buildTree_from_list(words,tree):
	# TODO: Merge these functions
	# Same as above, but builds from a list rather than a file
	# returns a handle for the tree object
	#print("Building search tree from: ",source)
	start = time.time()
	
	if tree == None:
		tree = NODE(None,None)

	#fp = open(source,"r")
	for word in words:
		#word = word.upper()
		#word = word.strip('\n')
		curr = tree
		for char in word:
			found = False
			for child in curr.children:
				# Search Children for existing node
				if child.char == char:
					# If found, move to that node and continue
					curr = child
					found = True
					break
			
			if found == False:
				# Didn't find the character, add a new node and continue
				nxt = NODE(char,curr)
				curr.children.append(nxt)
				curr = nxt
		# Mark the node as the end of a word
		curr.isEnd = True	

	stop = time.time()
	#print("\tFinished in: ",stop-start,"seconds")
	return tree

def findFull(word, tree):
	# Checks to see if word is in tree, returns true or false
	curr = tree
	for char in word:
		found = False
		for child in curr.children:
			if child.char == char:
				curr = child
				found = True
				break
		
		if found == False:
			return False
	return True

def searchWild(word,curr):
	# Recursive search function, searches all children for the first character in word
	matches = []
	for i in range(0,len(word)):
		# Search normally for word until wildcard character is encountered
		found = False

		if word[i] != '_':
			for child in curr.children:
				if child.char == word[i]:
					curr = child
					found = True
					break
		
		else:
			# Encountered wildcard, branch off on all children		
			for child in curr.children:
				ret = searchWild(word[i+1:],child)
				# Append any matches to list
				for match in ret:
					matches.append(match)


		if found == False:
			# Couldn't find character, return matches (if any)
			return matches
	if curr.isEnd:
		matches.append(curr)

	return matches

def searchWildTF(word,curr):
	# Recursive search function, searches all children for the first character in word
	# Same as previous version, but only runs till it finds a valid word, then returns 
	# True or False
	matches = []
	for i in range(0,len(word)):
		# Search normally for word until wildcard character is encountered
		found = False

		if word[i] != '_':
			for child in curr.children:
				if child.char == word[i]:
					curr = child
					found = True
					break
		
		else:
			# Encountered wildcard, branch off on all children		
			for child in curr.children:
				ret = searchWildTF(word[i+1:],child)
				# Append any matches to list
				if ret:
					return True

		if found == False:
			# Couldn't find character, return matches (if any)
			return False
	
	if curr.isEnd:
		return True

	return matches

def climbUp(curr):
	# Assembles a word by climbing up from whatever node is passed in
	# Returns the full string
	word = ""
	while curr.parent != None:
		word += curr.char
		curr = curr.parent
	#print(word[::-1])
	return word[::-1]
