# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import re
# Create your views here.

def index(request):
	if request.method == 'POST':
		commands = request.POST['commands']
		cmdarr = commands.splitlines()
		output = []
		hexoutput = []
		rangeLength = []

		for command in cmdarr:
			cmd = str(command.split(" ", 1)[0])
			var1 = str(re.split(', ', command.split(" ", 1)[1])[0].split("R", 1)[1])

			if cmd == "LD" or cmd == "SD":
				var2 = str(re.split(', |\(|\)', command.split(" ", 1)[1])[1])
			else:
				var2 = str(re.split(', ', command.split(" ", 1)[1])[1].split("R", 1)[1])

			if cmd == "LD" or cmd == "SD":
				var3 = str(re.split(', |\(|\)', command.split(" ", 1)[1])[2].split("R", 1)[1])
			else:
				var3 = str(re.split(r'R|#', re.split(', ', command.split(" ", 1)[1])[2])[1])

			if cmd == "LD":
				output.append('110111'+ format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0], 16), '04b') + format(int(var2[1], 16), '04b') + format(int(var2[2], 16), '04b') + format(int(var2[3], 16), '04b'))

			elif cmd == "SD":
				output.append('111111' + format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0]), '04b') + format(int(var2[1]), '04b') + format(int(var2[2]), '04b') + format(int(var2[3]), '04b'))

			elif cmd == "DADDIU":
				output.append('011001' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

			elif cmd == "XORI":
				output.append('001110' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

			elif cmd == "DADDU":
				output.append('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101101')

			elif cmd == "SLT":
				output.append('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101010')

			hexoutput.append(str(format(int(output[-1], 2), '08x')).upper())

		for i in range(len(cmdarr)):
			rangeLength.append(i)

		context = {
			'commands': commands,
			'cmdarr': cmdarr,
			'output': output,
			'hexoutput': hexoutput,
			'rangeLength': rangeLength,
		}
		return render(request, 'processor/index.html', context)
	
	return render(request, 'processor/index.html')
