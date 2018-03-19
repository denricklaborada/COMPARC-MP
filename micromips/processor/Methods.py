import re

def binToHex(binary):
	return str(format(int(binary, 2), '08x')).upper()

def opcode(command):
	cmd = getCommand(command)
	var1 = getFirstParam(command)
	var2 = getSecondParam(command)
	var3 = getThirdParam(command)

	if cmd == "LD":
		return('110111'+ format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0], 16), '04b') + format(int(var2[1], 16), '04b') + format(int(var2[2], 16), '04b') + format(int(var2[3], 16), '04b'))

	elif cmd == "SD":
		return('111111' + format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0]), '04b') + format(int(var2[1]), '04b') + format(int(var2[2]), '04b') + format(int(var2[3]), '04b'))

	elif cmd == "DADDIU":
		return('011001' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

	elif cmd == "XORI":
		return('001110' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

	elif cmd == "DADDU":
		return('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101101')

	elif cmd == "SLT":
		return('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101010')
        
def getCommand(given):
	return str(given.split(" ", 1)[0])

def getFirstParam(given):
	return str(re.split(', ', given.split(" ", 1)[1])[0].split("R", 1)[1])

def getSecondParam(given):
	cmd = getCommand(given)

	if cmd == "LD" or cmd == "SD":
		return str(re.split(', |\(|\)', command.split(" ", 1)[1])[1])

	return str(re.split(', ', given.split(" ", 1)[1])[1].split("R", 1)[1])

def getThirdParam(given):
	cmd = getCommand(given)

	if cmd == "LD" or cmd == "SD":
		return str(re.split(', |\(|\)', command.split(" ", 1)[1])[2].split("R", 1)[1])

	return str(re.split(r'R|#', re.split(', ', command.split(" ", 1)[1])[2])[1])
