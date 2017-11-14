# Create a massive english language trie
from searchTree import *
from setupFunctions import *
import pickle

sources = ["00english.txt",
		   "00english1.txt",
		   "00english2.txt",
		   "00english3.txt"]

tree = None

for source in sources:
	tree = buildTree(source,tree)

patDict = None

for source in sources:
	patDict = buildDict(source,patDict)


pickle.dump(tree,open("AllEng_tree.p","wb"))
pickle.dump(patDict,open("AllEng_pats.p","wb"))

#while True:
#	sel = str(input("Input a word to search for, _ is wild...\n")).upper()
#	print(findFull(sel,tree))
# 	print(sel,searchWild(sel,tree))
