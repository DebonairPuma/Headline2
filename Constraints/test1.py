from constraint import *

def myFunc(*arg):
	print arg
	return True

	if a > b and b >c:
		return True
	else:
		return False

p = Problem()
p.addVariables(['a','b','c'],[1,2,3,4])
p.addConstraint(myFunc,['a','b','c'])


print(p.getSolutions())