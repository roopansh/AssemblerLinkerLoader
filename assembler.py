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
                    assemblycode.append("JMP #" + str(location_counter + 4))
                    assemblycode.append("DB " + str(var2))
                    symtab[filename][var1] = "#" + str(location_counter + 3)
                    globtab[filename][var1] = "#" + str(location_counter + 3)
                    location_counter = location_counter + optab["JMP"] + 1
                else:
                    assemblycode.append("JMP #" + str(location_counter + 4))
                    symtab[filename][var1] = "#" + str(location_counter + 3)
                    globtab[filename][var1] = "#" + str(location_counter + 3)
                    assemblycode.append("LDA " + str(symtab[filename][var2]))
                    assemblycode.append("STA " + str(symtab[filename][var1]))
                    location_counter = location_counter + optab["JMP"] + optab["LDA"] + optab["STA"] + 1

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
                    error = "syntax error =>  " + line
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
                    error = "syntax error =>  " + line
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

            elif remul.match(line):
                var1 = remul.match(line).group(1)
                var2 = remul.match(line).group(2)
                var3 = remul.match(line).group(3)
                if isint(var1) or var1 not in symtab[filename]:
                    error = "syntax error =>  " + line
                    return
                # c = 3*5
                if isint(var2) and isint(var3):
                    assemblycode.append("MVI B,0")
                    assemblycode.append("MVI A," + str(var3))
                    location_counter = location_counter + optab["MVI"] + optab["MVI"]
                    assemblycode.append("JZ #" + str(location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +optab["MOV"] + optab["SUI"] + optab["JMP"]))
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("ADD B")
                    assemblycode.append("MOV B,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("SUI 1")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,B")
                    assemblycode.append("STA " +' # ' + str(var1))
                    location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # c = 3*a
                elif isint(var2):
                    if var3 not in symtab[filename]:
                        error = "syntax error =>  " + line
                        return
                    assemblycode.append("MVI B,0")
                    assemblycode.append("LDA " + +' # ' + str(var3))
                    location_counter = location_counter + optab["MVI"] + optab["LDA"]
                    assemblycode.append("JZ #" + str(
                        location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +
                        optab["MOV"] + optab["SUI"] + optab["JMP"]))
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("ADD B")
                    assemblycode.append("MOV B,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("SUI 1")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,B")
                    assemblycode.append("STA " + +' # ' + str(var1))
                    location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # c = b*3
                elif isint(var3):
                    if var2 not in symtab[filename]:
                        error = "syntax error =>  " + line
                        return
                    assemblycode.append("MVI B,0")
                    assemblycode.append("LDA " + ' # ' + str(var2))
                    location_counter = location_counter + optab["MVI"] + optab["LDA"]
                    assemblycode.append("JZ #" + str(
                        location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +
                        optab["MOV"] + optab["SUI"] + optab["JMP"]))
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MVI A," + str(var3))
                    assemblycode.append("ADD B")
                    assemblycode.append("MOV B,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("SUI 1")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,B")
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # c = a*b
                else:
                    if var2 not in symtab[filename] or var3 not in symtab[filename]:
                        error = "syntax error =>  " + line
                        return
                    assemblycode.append("MVI B,0")
                    assemblycode.append("LDA " + ' # ' + str(var2))
                    location_counter = location_counter + optab["MVI"] + optab["LDA"]
                    assemblycode.append("JZ #" + str(
                        location_counter + optab["JZ"] + optab["MOV"] + optab["LDA"] + optab["ADD"] + optab["MOV"] +
                        optab["MOV"] + optab["SUI"] + optab["JMP"]))
                    assemblycode.append("MOV C,A")
                    assemblycode.append("LDA " +' # ' + str(var3))
                    assemblycode.append("ADD B")
                    assemblycode.append("MOV B,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("SUI 1")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,B")
                    assemblycode.append("STA " + ' # ' + str(var1))
                    location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["LDA"] + optab["ADD"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab["STA"]

            elif rediv.match(line):
                var1 = rediv.match(line).group(1)
                var2 = rediv.match(line).group(2)
                var3 = rediv.match(line).group(3)
                if isint(var1) or var1 not in symtab[filename]:
                    error = "Invalid line: " + line
                    return
                # a = 6/3
                if isint(var2) and isint(var3):
                    assemblycode.append("MVI B," + str(var3))
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("SUB B")
                    assemblycode.append("MVI C,0")
                    location_counter = location_counter + optab["MVI"] + optab["MVI"] + optab["SUB"] + optab["MVI"]
                    assemblycode.append("JM #" + str(
                        location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
                        optab["MOV"] + optab["SUB"] + optab["JMP"]))
                    assemblycode.append("MOV F,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("ADI 1")
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MOV A,F")
                    assemblycode.append("SUB B")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,C")
                    assemblycode.append("STA " +  ' # ' + str(var1))
                    location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # a = 6/b
                elif isint(var2):
                    if var3 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("LDA " + ' # ' + str(var3))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("MVI A," + str(var2))
                    assemblycode.append("SUB B")
                    assemblycode.append("MVI C,0")
                    location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["MVI"] + optab["SUB"] + optab["MVI"]
                    assemblycode.append("JM #" + str(
                        location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
                        optab["MOV"] + optab["SUB"] + optab["JMP"]))
                    assemblycode.append("MOV F,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("ADI 1")
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MOV A,F")
                    assemblycode.append("SUB B")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,C")
                    assemblycode.append("STA " +  ' # ' + str(var1))
                    location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # a = b/6
                elif isint(var3):
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("MVI B," + str(var3))
                    assemblycode.append("LDA " +  ' # ' + str(var2))
                    assemblycode.append("SUB B")
                    assemblycode.append("MVI C,0")
                    location_counter = location_counter + optab["MVI"] + optab["LDA"] + optab["SUB"] + optab["MVI"]
                    assemblycode.append("JM #" + str(
                        location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
                        optab["MOV"] + optab["SUB"] + optab["JMP"]))
                    assemblycode.append("MOV F,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("ADI 1")
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MOV A,F")
                    assemblycode.append("SUB B")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,C")
                    assemblycode.append("STA " +  ' # ' + str(var1))
                    location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                # a = c/d
                else:
                    if var2 not in symtab[filename] or var3 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("LDA " +  ' # ' + str(var3))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA " +  ' # ' + str(var2))
                    assemblycode.append("SUB B")
                    assemblycode.append("MVI C,0")
                    location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + optab["MVI"]
                    assemblycode.append("JM #" + str(
                        location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
                        optab["MOV"] + optab["SUB"] + optab["JMP"]))
                    assemblycode.append("MOV F,A")
                    assemblycode.append("MOV A,C")
                    assemblycode.append("ADI 1")
                    assemblycode.append("MOV C,A")
                    assemblycode.append("MOV A,F")
                    assemblycode.append("SUB B")
                    assemblycode.append("JMP #" + str(location_counter))
                    assemblycode.append("MOV A,C")
                    assemblycode.append("STA " +  ' # ' + str(var1))
                    location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab[
                        "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab["STA"]
                        # if a < b 

            # if a < b 
            elif reiflt.match(line):
                var1 = reiflt.match(line).group(1)
                var2 = reiflt.match(line).group(2)

                # if 2 < 3 
                if isint(var1) and isint(var2):
                    # ACC <-- 2 - 3
                    assemblycode.append("MVI A," + str(var1))
                    assemblycode.append("SUI " + str(var2))
                    # if SIGN BIT is 0 (i.e. positive)
                    assemblycode.append("JP &&&" + str(ifs))
                    # if ZERO BIT is 1 
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab['MVI'] + optab['SUI'] + optab['JP'] + optab['JZ']

                # if 2 < b
                elif isint(var1):
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                   
                    # ACC <-- b - 2
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("SUI " + str(var1))
                    # if SIGN BIT is 1 (negative)
                    assemblycode.append("JM &&&" + str(ifs))
                    # if ZERO BIT is 1 
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['JM'] + optab['JZ']
                
                # if a < 3
                elif isint(var2):
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return

                    # ACC <-- a - 3
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    assemblycode.append("SUI " + str(var2))
                    # if SIGN BIT is 0 (positive)
                    assemblycode.append("JP &&&" + str(ifs))
                    # if ZERO BIT is 1 
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['JP'] + optab['JZ']
                
                # if a < b
                else:
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return

                    # ACC <-- a - b
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    # ACC <-- a - b
                    assemblycode.append("SUB B")
                    # if SIGN BIT is 0 (positive)
                    assemblycode.append("JP &&&" + str(ifs))
                    # if ZERO BIT is 1 
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + optab["JP"] + optab["JZ"]

            # if a > b
            elif reifgt.match(line):
                var1 = reifgt.match(line).group(1)
                var2 = reifgt.match(line).group(2)

                # if 3 > 2
                if isint(var1) and isint(var2):
                    # ACC <-- 3 - 2
                    assemblycode.append("MVI A," + str(var1))
                    assemblycode.append("SUI " + str(var2))
                    # if SIGN BIT is 1 (negative)
                    assemblycode.append("JM &&&" + str(ifs))
                    # if ZERO BIT is 1
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["MVI"] + optab["SUI"] + optab["JM"] + optab["JZ"]

                # if 3 > b
                elif isint(var1):
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return

                    # ACC <-- b - 3
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("SUI " + str(var1))
                    # if SIGN BIT is 0 (positive)
                    assemblycode.append("JP &&&" + str(ifs))
                    # if ZERO BIT is 1
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JP"] + optab["JZ"]
                    
                # if a > 2
                elif isint(var2):
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return

                    # ACC <-- a - 2
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    assemblycode.append("SUI " + str(var2))
                    # if SIGN BIT is 1 (negative)
                    assemblycode.append("JM &&&" + str(ifs))
                    # if ZERO BIT is 1
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JM"] + optab["JZ"]
                
                # if a > b
                else:
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return

                    # ACC <-- a - b
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    assemblycode.append("SUB B")
                    # if SIGN BIT is 0 (postive)
                    assemblycode.append("JM &&&" + str(ifs))
                    # if ZERO BIT is 1
                    assemblycode.append("JZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + optab["JM"] + optab["JZ"]
            
            # if a = b 
            elif reifeq.match(line):
                var1 = reifeq.match(line).group(1)
                var2 = reifeq.match(line).group(2)

                # if 2 = 2
                if isint(var1) and isint(var2):
                    assemblycode.append("MVI A," + str(var1))
                    assemblycode.append("SUI " + str(var2))
                    assemblycode.append("JNZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["MVI"] + optab["SUI"] + optab["JNZ"]

                # if 2 = a
                elif isint(var1):
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("SUI " + str(var1))
                    assemblycode.append("JNZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JNZ"]

                # if a = 2
                elif isint(var2):
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    assemblycode.append("SUI " + str(var2))
                    assemblycode.append("JNZ &&&" + str(ifs))
                    openifs = openifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JNZ"]
                
                # if a = b
                else:
                    if var2 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    if var1 not in symtab[filename]:
                        error = "Invalid line: " + line
                        return
                    assemblycode.append("LDA #" + str(symtab[filename][var2]))
                    assemblycode.append("MOV B,A")
                    assemblycode.append("LDA #" + str(symtab[filename][var1]))
                    assemblycode.append("SUB B")
                    assemblycode.append("JNZ &&&" + str(ifs))
                    ifs = ifs + 1
                    location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + optab["JNZ"]
            
            # endif
            elif reendif.match(line):
                iftable[ifs - 1] = location_counter

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

        assemblycode = '\n'.join(assemblycode)
        print(assemblycode)


def pass2(pass1Code):
    for line in pass1Code:
        if "&&&" not in line and "!!!" not in line and "~~~" not in line:
            assco.append(line)
        elif "&&&" in line:
            ifp = line.split("&&&")[1]
            ifp = int(ifp)
            line = line.replace("&&&"+line.split("&&&")[1], "#" + str(iftable[ifp]))
            assco.append(line)
        elif "!!!" in line:
            fnp = line.split("!!!")[1]
            fnp = int(fnp)
            line = line.replace("!!!"+line.split("!!!")[1], "#" + str(fcalls[fnp]))
            assco.append(line)
        else:
            jc = line.split("~~~")[1]
            line = line.replace("~~~" + line.split("~~~")[1], str(symtab[filename][jc]))
            assco.append(line)
