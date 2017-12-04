def getKey(inStr,tryRev):
	# Given an input string, finds the correct decimation and returns the matrix containing it
	print("Getting KEY from:")
	print("-->",inStr,"\n")

	# Create use dict
	alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	uDict = {}
	for letter in alpha:
		uDict[letter] = False

	decVals = [1,3,5,7,9,11]
	hatLengths = [7,8,9,10,11,12]

	# Characters to begin search with, One of these is nearly guaranteed to start one of the long strings
	startingChars = ['Z','Y','X','W','V','T']

	# Try all decimations
	for decimation in decVals:
		print("\nChecking Decimation: ",decimation)
		# Get Decimatino
		curr = decimate(decimation,inStr)
		print("\t",curr,"\n")

		# Try all hat lengths
		for hatL in hatLengths:
			print("\tChecking Hat Length:",hatL)
			# Loop through starting chars:
			for initial in startingChars:
				# Reset use dict:
				for letter in alpha:
					uDict[letter] = False

				# Reset array of strings
				strMat = []
				val = getSlice(curr,uDict,initial,26/hatL +1)# num chars in long set determined by hatL
				if val == False:
					# Shouldn't happen
					continue
				else:
					strMat.append(val[0])
					uDict = val[1]

				# Grab next string:
				ret = grabNextStr(curr,uDict,strMat,26%hatL,False)

				if ret == False:
					# Unsuccessful try next starting char:
					continue
				else:
					# Success! At least so far
					strMat = ret[0]
					uDict = ret[1]

					# Get the first short slice, must be alphabetically after the last one
					pos = alpha.find(strMat[0][-2])
					for i in range(pos,len(alpha)):
						val = getSlice(curr,uDict,alpha[i],len(strMat[0])-1)
						if val == False:
							continue
						else:
							shortMat = [val[0]]
							tDict = val[1]
							ret = grabNextStr(curr,tDict,shortMat,hatL-(26%hatL),True)
							if ret == false:
								continue
							else:
								print("\n\t\tSUCCESS!\n")
								finalMat = []

							for i in range(0,len(strMat)):
								finalMat.append(strMat[len(strMat)-(1+i)])

							for line in ret[0]:
								finalMat.append(line)

							# Print Results

							# print "final mat",finalMat

							for i in range(0,len(finalMat[0])):
								tStr = ''
								for j in range(0,len(finalMat)):
									try:
										tStr += finalMat[j][i]
									except:
										pass
								print("\t\t",tStr)

							numKey = getNumKey(curr,finalMat)

							return (finalMat,numKey)

	# Failed, try with reverse string
	if tryRev == True:
		print("FAILED! Attempting with reversed string")
		return getKey(inStr[::-1],False)
	else:
		print("FAILED AGAIN! Manually Check?")
		return (False)

def getNumKey(inStr,inMat):
	# given a string and a matrix, returns the numeric key
	# Verify that entire first string is in position, if not
	# Circular shift right until it appears:
	print("\n\t\tEvaluating Key")
	found = False
	
	while True:
		for block in inMat:
			if block == inStr[0:len(block)]:
				found = True
				break

		if found == False:
			# need to rotate string
			print("WARNING: In getNumKey, needed to rotate string! Key may be invalid!")
			inStr = inStr[-1] + inStr[0:len(inStr)-1]
		else:
			break

	# Now determine the key:
	pos = 0
	key = [0]*len(inMat)
	while len(inStr) != 0:
		for i in range(0,len(inMat)):
			if inMat[i] == inStr[0:len(inMat[i])]:
				key[i] = pos+1
				pos +=1
				inStr = inStr[len(inMat[i]):]
	print("\t\tDone!\n")
	return key			

def grabNextStr(curr,uDict,strMat,depth,short):
	# Tries to grab the next string, if valid, calls itself and continues
	# Depth is the number of strings we want to have in strMat
	# Short is a flag that reverses search direction and disables the second
	# alphabetical check so we can search for short strings

	# Verify that we're not already done, should only happen in special case:
	if len(strMat) == depth:
		return (strMat,uDict)

	alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	if short == False:
		alpha = alpha[::-1]

	# get current character in alphabetical order:
	pos = alpha.find(strMat[-1][-1])

	# Grab the next possible string
	for i in range(pos,len(alpha)):
		# Try to grab the next string:
		val = getSlice(curr,uDict,alpha[i],len(strMat[0]))
		if val == False:
			# if this fails, go ahead and try the next starting char
			continue
		else:
			# Determine whether or not to proceed:
			if short == False:
				# if we're looking for long strings, we can make this check
				proceed = checkOrder(val[0][-2],strMat[-1][-2])
			else:
				# If we're looking for shorter strings proceed regardless
				proceed = True

			# Verify that second characters are in order
			if proceed:
				# if so, update and call grab next str
				# This may be overly cautious:
				tDict = val[1]
				tMat = strMat
				tMat.append(val[0])

				if len(tMat) == depth:
					# tMat is the right depth, we're done here, return successful
					return (tMat,tDict)
				else:
					# Need to use recursion:
					ret = grabNextStr(curr,tDict,tMat,depth,short)
					if ret == False:
						# Couldnn't find a valid string, keep trying
						continue
					else:
						# End of recursion, return to top
						return (ret[0],ret[1])
			else:
				# continue? Could probably abort, but just in case
				continue

	# if we've made it here, it's clearly failed:
	return False

# Decimate String
def decimate(value,inStr):
	ret = ""
	pos = 0
	while len(ret)<26:
		ret = ret + inStr[pos%26]
		pos = pos+value
	return ret

def checkOrder(a,b):
	# returns true iff inputs are in alphabetical order
	alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	if alpha.find(a) < alpha.find(b):
		return True
	else:
		return False

def getSlice(decStr,uDict,letter,numChars):
	# Attempts to slice off numChars letters from decStr starting at letter
	# if successful, returns the slice and the update inUse list
	# on failure (string is already in use, or can't get that block) returns false
	# will wrap around start to finish

	# Get starting point:
	pos = decStr.find(letter)

	# Temporarily slice array so we're guaranteed to get the entire thing:
	tmp = decSTr[pos+1:]+decStr[0:pos+1]

	# Make the slice:
	outStr = tmp[len(decStr)-numChars:]

	# Verify that no characterse in slice have already been used:
	for char in outStr:
		if uDict[char] == True:
			# Char in use, return false
			return False

	# Set the chars in uDict
	for char in outStr:
		uDict[char] = True

	return (outStr,uDict)
