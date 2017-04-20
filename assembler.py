import re

symtab = {}
optab = {}
littab = {}
pooltab = []


def findoptab():
    with open("opcodes.txt", "r") as file:
        opcodes = file.read().split("\n")
        file.close()
    for opcode in opcodes:
        opcode = opcode.lstrip().rstrip()
        if opcode != '':
            optab[opcode.split()[0]] = int(opcode.split()[1])


def isint(string):
    try:
        int(string)
        return True
    except:
        return False


def pass1(fileNames):
    global error
    global optab
    global symtab
    global globtab
    global littab
    global pooltab
    global filelentable
    global location_counter
    global pooltab_counter

    optab = {}
    symtab = {}
    littab = {}
    pooltab = []
    globtab = {}
    filelentable = {}
    error = "False"

    findoptab()

    revar = re.compile("var\s+(\w+)\s*=\s*(\w+)\s*")
    reglo = re.compile("global\s+var\s+(\w+)\s*=\s*(\w+)\s*")
    replus = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)\s*")
    reminus = re.compile("\s*(\w+)\s*=\s*(\w+)\s*-\s*(\w+)\s*")
    remul = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)\s*")
    rediv = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\/\s*(\w+)\s*")

    reand = re.compile("\s*(\w+)\s*=\s*(\w+)\s*&\s*(\w+)\s*")
    reor = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\|\s*(\w+)\s*")

    for filenam in fileNames:
        with open(filenam, 'r') as file:
            code = file.read()
            lines = code.split('\n')
            file.close()

        filename = filenam.split('.')[0]

        pooltab_counter = 0
        location_counter = 0
        # update location counter in start statment.

        assemblycode = []
        symtab[filename] = {}
        littab[filename] = []
        globtab[filename] = {}

        for line in lines:
            line = line.lstrip().rstrip()

            if reglo.match(line):
                var1 = reglo.match(line).group(1)
                var2 = reglo.match(line).group(2)
                if (not isint(var2) and var2 not in symtab[filename]) or isint(var1):
                    error = "Variable " + var2 + " not declared" + "in" + line
                    return
                if isint(var1):
                    error = "Expected variable" + "in" + line
                if isint(var2):
                    assemblycode.append("JMP #" + str(memadd + 4))
                    assemblycode.append("DB " + str(var2))
                    symtab[filename][var1] = "#" + str(memadd + 3)
                    globtab[filename][var1] = "#" + str(memadd + 3)
                    memadd = memadd + optab["JMP"] + 1
                else:
                    assemblycode.append("JMP #" + str(memadd + 4))
                    symtab[filename][var1] = "#" + str(memadd + 3)
                    globtab[filename][var1] = "#" + str(memadd + 3)
                    assemblycode.append("LDA " + str(symtab[filename][var2]))
                    assemblycode.append("STA " + str(symtab[filename][var1]))
                    memadd = memadd + optab["JMP"] + optab["LDA"] + optab["STA"] + 1

            elif revar.match(line):
                var1 = revar.match(line).group(1)
                var2 = revar.match(line).group(2)

                if (not isint(var2) and var2 not in symtab[filename]) or isint(var1):
                    error = "Variable " + var2 + " not declared" + "in" + line
                    return
                if isint(var1):
                    error = " Syntax error => Expected variable " + "in" + line

                if isint(var2):
                    symtab[filename][var1] = location_counter
                    pooltab.append(pooltab_counter)
                    littab[filename].append((var2, location_counter))
                    pooltab_counter = pooltab_counter + 1

                else:
                    assemblycode.append("LDA " + '#' + str(var2))  # load to accumulator
                    assemblycode.append("STA " + '#' + str(var1))  # load from accumulator
                    symtab[filename][var1] = location_counter
                    location_counter = location_counter + optab['LDA'] + optab['STA']


            # var1 =var2 +var3
            elif replus.match(line):
                var1 = replus.match(line).group(1)
                var2 = replus.match(line).group(2)
                var3 = replus.match(line).group(3)
                if isint(var1) or var1 not in symtab[filename]:
                    error = "Invalid line: " + line
                    return

                # e.g-a=2+3
                if isint(var2) and isint(var3):
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("ADI " + str(var3))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['MVI'] + optab['ADI'] + optab['STA']

                # eg- a=2+b
                elif isint(var2):
                    if var3 not in symtab[filename]:
                        error = "Variable " + var3 + " not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var3))
                    assemblycode.append("ADI " + str(var2))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['ADI'] + optab['STA']

                # eg- a=b+2
                elif isint(var3):
                    if var2 not in symtab[filename]:
                        error = "Variable " + var3 + " not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var2))
                    assemblycode.append("ADI " + str(var3))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['ADI'] + optab['STA']

                # eg a=b+c
                else:
                    if var2 not in symtab[filename] or var3 not in symtab[filename]:
                        error = "Variable not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var2))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA " + '#' + str(var3))
                    assemblycode.append("ADD B")
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['ADD'] + \
                                       optab['STA']


            elif reminus.match(line):
                var1 = replus.match(line).group(1)
                var2 = replus.match(line).group(2)
                var3 = replus.match(line).group(3)
                if isint(var1) or var1 not in symtab[filename]:
                    error = "Invalid line: " + line
                    return

                # e.g-a=2-3
                if isint(var2) and isint(var3):
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("SUI " + str(var3))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['MVI'] + optab['SUI'] + optab['STA']

                # eg- a=2-b
                elif isint(var2):
                    if var3 not in symtab[filename]:
                        error = "Variable " + var3 + " not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var3))
                    assemblycode.append("SUI " + str(var2))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['STA']

                # eg- a=b-2
                elif isint(var3):
                    if var2 not in symtab[filename]:
                        error = "Variable " + var3 + " not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var2))
                    assemblycode.append("SUI " + str(var3))
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['STA']

                # eg a=b-c
                else:
                    if var2 not in symtab[filename] or var3 not in symtab[filename]:
                        error = "Variable not declared in " + line
                        return

                    assemblycode.append("LDA " + ' # ' + str(var2))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA " + '#' + str(var3))
                    assemblycode.append("SUB B")
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['SUB'] + \
                                       optab['STA']


        # all lines have been passed in pass1
        assemblycode.append(" END ")
        for i,literal in enumerate(littab[filename]):

            literal = (literal[0], location_counter)
            littab[filename][i]=literal

            for var in symtab:
                if(symtab[var] ==literal[1]):
                    symtab[var] =location_counter
                    break

            assemblycode.append("='" + str(literal[0]) +"'" )
            location_counter = location_counter + 4

        print(assemblycode)
