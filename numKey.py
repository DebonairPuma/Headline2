import string
import itertools


class letter():
	def __init__(self,char,parent,canMatch):
		self.char = char
		self.parent = parent
		self.child = None
		self.canMatch = canMatch
	def addChild(self,child):
		self.child = child
	def setChar(self,char):
		self.char = char


alpha = string.ascii_letters[:26].upper()

hat = [5,8,1,6,10,2,9,3,7,4]

seq = [letter(None,None,None) for x in hat]
root = letter(None,None,False)

nxt = 1
curr = None
# Link the correct elements of list (list of nodes in numeric order, as opposed to the order they
# should be in the actual word)
while nxt <len(hat)+1:
	canMatch = False
	for i in range(0,len(hat)):
		if hat[i] == nxt:
			# If we found the one
			if curr == None:
				seq[i].parent = root
				root.addChild(seq[i])
				seq[i].canMatch = True
						
			else:
				seq[i].parent = seq[curr]	
				seq[curr].addChild(seq[i])
				seq[i].canMatch = canMatch
				
			canMatch = True
			curr = i
			nxt += 1


L1 = {'a','b','c','d'}
L2 = {'h','g','f','e'}
L3 = {'w','x','y','z'}
L4 = {'l','m','n','o'}
L5 = {'q','r','s','t'}

hat = [3,1,5,4,2]
#	   a b c d e  f g h i j
hat = [5,8,1,6,10,2,9,3,7,4]
valid = []

print("starting")
dst = open("validkeys.txt","w")
for a in range(1,26):
	print(".")
	for b in range(2,26):
		for c in range(0,26):
			print("c dot")
			for d in range(0,26):
				print("d dot")
				for e in range(4,26):
					for f in range(0,26):
						for g in range(2,26):
							for h in range(0,26):
								for i in range(1,26):
									for j in range(0,26):
										if j >= h and i >= d and h >= f and g > b and f >= c and e > g and d >= a and b > i:
											valid.append(alpha[a]+alpha[b]+alpha[c]+alpha[d]+alpha[e]+alpha[f]+alpha[g]+alpha[h]+alpha[i]+alpha[j])
				print("writing ", len(valid),"items")
				for item in valid:
					dst.write(item)
				valid = []


dst.close()


#print(itertools.product(L1,L2))

#print(list(itertools.permutations(L1,L2)))