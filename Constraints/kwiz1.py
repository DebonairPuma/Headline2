from constraint import *

def c0(D,E,F,G,DIV):
	try:
		if DIV == 'ADD':
			return (((E*10 + F) + D) == (G*10 + E))
		elif DIV == 'SUB':
			return (((E*10 + F) - D) == (G*10 + E))
		elif DIV == 'MUL':
			return (((E*10 + F) * D) == (G*10 + E))
		elif DIV == 'DIV':
			return (((E*10 + F) / D) == (G*10 + E))
	except:
		return False

def c1(A,B,G,E,H,MUL):
	try:
		if MUL == 'ADD':
			return (((G*10 + G) + A) == ((E*100) + (B*10) + H))
		elif MUL == 'SUB':
			return (((G*10 + G) - A) == ((E*100) + (B*10) + H))
		elif MUL == 'MUL':
			return (((G*10 + G) * A) == ((E*100) + (B*10) + H))
		elif MUL == 'DIV':
			return (((G*10 + G) / A) == ((E*100) + (B*10) + H))
	except:
		return False

def c2(C,E,I,J,ADD):
	try:
		if ADD == 'ADD':
			return (((I*10 + C) + J) == (E*10 + J))
		elif ADD == 'SUB':
			return (((I*10 + C) - J) == (E*10 + J))
		elif ADD == 'MUL':
			return (((I*10 + C) * J) == (E*10 + J))
		elif ADD == 'DIV':
			return (((I*10 + C) / J) == (E*10 + J))
	except:
		return False

def c3(E,G,I,J,SUB):
	try:
		if SUB == 'ADD':
			return (((E*10 + J) + I) == (G))
		elif SUB == 'SUB':
			return (((E*10 + J) - I) == (G))
		elif SUB == 'MUL':
			return (((E*10 + J) * I) == (G))
		elif SUB == 'DIV':
			return (((E*10 + J) / I) == (G))		
	except:
		return False

p = Problem()
p.addVariables(['a','b','c','d','e','f','g','h','i','j'],[0,1,2,3,4,5,6,7,8,9])
p.addVariables(["add","sub","mul","div"],["ADD","SUB","MUL","DIV"])
p.addConstraint(AllDifferentConstraint())
p.addConstraint(c0,['d','e','f','g','div'])
p.addConstraint(c1,['a','b','g','e','h','mul'])
p.addConstraint(c2,['c','e','i','j','add'])
p.addConstraint(c3,['e','g','i','j','sub'])
print(p.getSolutions())


