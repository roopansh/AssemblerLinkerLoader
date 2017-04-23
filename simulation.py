import sys


reg = {}
reg['A'] = 0
reg['B'] = 0
reg['C'] = 0
reg['D'] = 0
reg['E'] = 0
reg['F'] = 0
reg['G'] = 0
reg['H'] = 0
reg['PC'] = 0


reg['SP'] = 0
PC = 0
stack = []

oplen = {}
dbloc = []

def calculatelen():
	inputFile = open('opcodes.cf',"r")
	code = inputFile.read()
	lines = code.split('\n')
	for line in lines :
		line = line.lstrip().rstrip()
		if line != '' :
			oplen[line.split(' ')[0]] = int(line.split(' ')[1])

calculatelen()
memory = {}

def load(filename, offset):
	inputFile = open(filename,"r")
	code = inputFile.read()
	lines = code.split('\n')
	mem = offset
	for line in lines :
		op = line.split(' ')[0].lstrip().rstrip()
		if op != 'DB':
			memory[mem] = line
			mem += oplen[op]
		else:
			memory[mem] = int(line.split(' ')[1].lstrip().rstrip())
			dbloc.append(mem)
			mem += 1

def simulator(pc = 0):
	inst = memory[pc]
	opcode = inst.split(' ')[0]
	global stack
	memlocs = ''
	for db in dbloc:
		memlocs += (str(db) + ' : ' + str(memory[db]) + '\n')

	# memstr.set(memlocs)
	print (memlocs)
	# raw_input("Press Enter to continue...")
	if opcode == 'HLT':
		# progcompleted.set('DONE')
		return
	elif opcode == 'JMP':
		nextinst = int(inst.split(' ')[1])
		PC = nextinst
		# print (nextinst)
		# print (PC)
	elif opcode == 'MVI':
		regvar = inst.split(' ')[1].split(',')[0].lstrip().rstrip()
		reg[regvar] = int(inst.split(' ')[1].split(',')[1].lstrip().rstrip())
		PC = pc + int(oplen[opcode])
	elif opcode == 'ADI':
		reg['A'] = int(reg['A']) + int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'STA':
		memloc = int(inst.split(' ')[1])
		memory[memloc] = int(reg['A'])
		PC = pc + int(oplen[opcode])
	elif opcode == 'LDA':
		memloc = int(inst.split(' ')[1])
		reg['A'] = int(memory[memloc])
		PC = pc + int(oplen[opcode])
	elif opcode == 'MOV':
		destreg = inst.split(' ')[1].split(',')[0].lstrip().rstrip()
		srcreg = inst.split(' ')[1].split(',')[1].lstrip().rstrip()
		reg[destreg] = reg[srcreg]
		PC = pc + int(oplen[opcode])
	elif opcode == 'ADD':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) + int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'SUI':
		reg['A'] = int(reg['A']) - int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'SUB':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) - int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ANI':
		reg['A'] = int(reg['A']) & int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ANA':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) & int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ORI':
		reg['A'] = int(reg['A']) | int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ORA':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) | int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'PUSH':
		srcreg = inst.split(' ')[1]
		stack.append(int(reg[srcreg]))
		PC = pc + int(oplen[opcode])
	elif opcode == 'POP':
		srcreg = inst.split(' ')[1]
		reg[srcreg] = stack.pop()
		PC = pc + int(oplen[opcode])
	elif opcode == 'JNZ':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) != 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == 'JZ':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) == 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == 'JP':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) > 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	reg['PC'] = PC

def callbackf():
	simulator(int(reg['PC']))