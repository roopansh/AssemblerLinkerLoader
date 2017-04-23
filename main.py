import assembler, linker, loader, simulation

x = []


def runass():
	assembler.pass1(x)

def runlin():
	linker.linker(x)

def runload(offset=0):
	loader.loader(x, offset)
	simulation.reg['PC'] = offset

def getSymTable():
	return assembler.symTable

def getGlobTable():
	return assembler.globTable

def getExtTable():
	return assembler.extTable

def getifTable():
	return assembler.ifTable

def runloader(file, offset=0):
	simulation.load(file, offset)

def runSimulator():
	simulation.callbackf()

def getRegisters():
	return simulation.reg

def getStack():
	return simulation.stack

def getMemlocs():
	return simulation.memory