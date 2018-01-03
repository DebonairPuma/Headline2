
	'''
	# Get only test strings for which all words are in the dictionary
	tencStrs = []
	tclrStrs = []
	for test in tests:
		for i in range(0,len(test.encStrs)):
			clrWords = test.clrStrs[i].split(" ")
			while "" in clrWords:
				clrWords.remove("")

			valid = True
			for word in clrWords:
				if findFull(word,tree):
					pass
				else:
					valid = False
					break
			#if valid == True:
			tencStrs.append(test.encStrs[i])
			tclrStrs.append(test.clrStrs[i])
	
	print("From ",len(tests)*5,"test cases, found",len(tencStrs),"which should be solvable")
	print("Trying set solver on all cases:")

	threshold = 10
	goodsolves = 0
	badsolves = 0
	ttrim = 0
	tsets = 0

	Textra = 0
	Sextra = 0
	tsolved = 0
	ssolved = 0
	tfailed = 0
	sfailed = 0

	for testStr in tencStrs:
		t1 = time.time()
		ret = selectWords2Trim2(testStr,patDict)
		t2 = time.time()
		ttrim += t2-t1
		tmp = 0
		for key in ret:
			if len(ret[key]) == 0:
				tfailed += 1
				break
			if len(ret[key]) != 1:
				tmp += len(ret[key]) - 1
				Textra += len(ret[key]) - 1
		if tmp < 15:
			if tmp != 0:
				tsolved+=1

		t1 = time.time()
		ret = setSolve(testStr,patDict)
		t2 = time.time()
		tsets += t2-t1
		tmp = 0
		for key in ret:
			if len(ret[key]) == 0:
				sfailed += 1
				break
			if len(ret[key]) != 1:
				tmp += len(ret[key]) - 1
				Sextra += len(ret[key]) - 1
		if tmp<15:
			if tmp != 0:
				ssolved+=1

	print("DONE!\n\tTrim Time: ",ttrim,"\n\tSets Time: ",tsets)
	print("\t\tTrim had ",Textra,"extraneous and", tsolved,"perfect or near perfect solves")
	print("\t\tSets had ",Sextra,"extraneous and", ssolved,"perfect or near perfect solves")
	print("\t\ttrim had ",tfailed,"failures")
	print("\t\tSets had ",sfailed,"failures")
	#print("Of ",len(tencStrs),"strings tested ", goodsolves,"strings were below the threshold of",threshold)
	'''

	'''
	words = encStrs[4].split(" ")
	while "" in words:
		words.remove("")

	# Get Matches
	matches = []
	for i in range(0,len(words)):
		matches.append(getMatches(words[i],patDict))

	print(matches[0])
	val = setSolve_slim(words,matches)
	print("############################################\n\n",matches[0])

	start = time.time()
	ss = SigSolver(words,matches)
	matches[0] = ss.sigTrim(0)
	stop = time.time()
	print("first pass",stop-start)
	
	start = time.time()
	selectWords2Trim2(encStrs[0],patDict)
	stop = time.time()
	print("sw2t2",stop-start)
	'''



	'''
	start = time.time()
	print(singleSetTrim_thorough(words,matches,0,1))
	trimmed1 = signature_main(words, matches, 0, patDict)
	stop = time.time()
	print("done in", stop-start)
	print(trimmed1)
	exit()
	start = time.time()
	results = signature_main(words, matches, 0, patDict)
	trimmed2 = singleSetTrim_thorough(words,matches,0,1)
	stop = time.time()
	print(len(matches[0]))
	print("done in", stop-start)

	matches[0] = list(results)
	print("here")
	print(matches[0])
	start = time.time()
	newlist = singleSetTrim_thorough(words,matches,0,1)
	print(newlist)
	stop = time.time()
	print("done in", stop-start)
	
	selSchars = list(get_shared_chars(words, 0))
	selSigsA = get_sig_sel(words[0],selSchars, newlist)
	print(selSigsA.keys())
	print()
	selSigsB = get_sig_sel(words[0],selSchars, results)
	print(selSigsB.keys())
	print()

	A = set(selSigsA.keys())
	B = set(selSigsB.keys())
	print(A ^ B)
	
	#HPQFRC BRFFSRB OQFJ EQIERC TGG MKBBRPDRU
	#UNITED SETTLES WITH KICKED OFF PASSENGER 
	#['Q', 'P', 'F', 'C', 'R']
	# Sigs from first round
	schars1 = list(get_shared_chars(words, 0))
	sigsel1 = get_sig_sel(words[0], schars1, trimmed1)
	print("sigs from first round")
	print(sigsel1.keys())
	print("sigs from second round round")

	schars2 = list(get_shared_chars(words, 0))
	sigsel2 = get_sig_sel(words[0], schars2, trimmed2)
	print(sigsel2.keys())
	'''

	'''
	# Runs single set solver on all tests
	for test in tests:
		headlines = []
		start = time.time()
		for i in range(0,len(test.encStrs)):
			headlines.append(HEADLINE(test.encStrs[i],patDict,None))
			for k in range(0,len(headlines[-1].encWords)):
				singleSetTrim_thorough(headlines[-1].encWords,headlines[-1].allMatches,k,1)
	
		stop = time.time()
		print("\tSet up headlines in:",stop-start,"seconds")


		#for i in range(0,len(test.encStrs)):
		#	print(test.clrStrs[i])	
	'''



	'''
	log = open("hardlines.txt","w")
	for test in tests:
		numPassed = 0
		start = time.time()
		for i in range(0,len(test.encStrs)):
			result = setSolve(test.encStrs[i],patDict)
			ret = evaluateresult(result)
			if ret == False:
				log.write(test.clrStrs[i]+"\n")
				log.write(test.encStrs[i]+"\n")
				
			else:
				if (ret[0]+ret[1]) > (ret[2] +ret[3]):
					numPassed +=1
		stop = time.time()
		print(test.handle,"Passed ",numPassed,"/5\n\t in ",stop-start,"seconds")
		print("*********************************************\n\n")
	'''
	
	



	'''
	# Attempt to figure out which words just aren't in the dictionary we're using:
	newWords = []
	for test in tests:
		for clrStr in test.clrStrs:
			words = clrStr.split(" ")
			for word in words:
				if findFull(word, tree) == False:
					newWords.append(word)
					print("Couldn't find: ",word)
	
	source = "customWords.txt"
	fp = open(source, "a")
	for word in newWords:
		fp.write(word+"\n")
	fp.close()
	'''

	'''
	#for line in encStrs:
	#	setSolve(line,patDict)
	#tstr = "LMWQLX NRQSKV QY SKXMLINVML ZLNHHMH LMEQLVMX OK JNG"
	tstr = "DXGUX NHQHAQ CHIHAYWP VYQX GXYW RCM"
	matches = []
	encWords = tstr.split(" ")
	for word in encWords:
		matches.append(getMatches(word,patDict))

	for mlist in matches:
		print(len(mlist))

	# Try 3,4,5 with this string
	for item in range(len(encWords)):
		if len(encWords[item])<4:
			continue
		print("Trying word:",encWords[item])
		print("Single Set:")
		ret = singleSetTrim(encWords,matches,item,1)
		if len(ret)<5:
			print(ret)
		print("Thorough:")
		ret = singleSetTrim_thorough(encWords,matches,item,1)
		if len(ret)<5:
			print(ret)
	# Initialize HEADLINE objects
	'''