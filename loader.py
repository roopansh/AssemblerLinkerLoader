def convert(filename, offset):
	with open(filename.split('.')[0] + '.linked', 'r') as file:
		lines = file.read().split('\n')
		file.close()

	asscode = []

	for line in lines:
		if '@' in line:
			varp = line.split("@")[1]
			# print(varp)
			varp = varp.split(',')
			# print(varp[0])
			varpe = varp[0]
			varpestripped = varpe.lstrip().rstrip()
			add = int(varpestripped)
			add = str(add + offset)
			# print ("add" + add)
			# print ( varp)
			# print ("varpe" + varpe)
			# print ("varprestr" + varpestripped)
			# print(line)
			line = line.replace('@' + varpestripped, "" + add)
			# print(line)
			asscode.append(line)
		else:
			asscode.append(line)

	asscode.append('HLT')

	with open(filename.split('.')[0] + '.loaded', 'w') as file:
		file.write('\n'.join(asscode))
		file.close()

convert('test1.linked',5000)
