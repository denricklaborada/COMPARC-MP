from __future__ import unicode_literals
from django.shortcuts import render, redirect
import re, binascii
from .models import Register, DataSegment, MipsProgram

def index(request):
	progObjects = MipsProgram.objects.all()
	error = False

	if request.method == 'POST':
		MipsProgram.objects.all().delete()

		try:
			commands = request.POST['commands']
			cmdarr = commands.splitlines()
			output = []
			hexoutput = []
			pipeline = []
			i = 0
			label = ''

			for index, command in enumerate(cmdarr):
				temp = []
				dependent = -1

				if ': ' in command:
					label = str(command.split(": ", 1)[0])
					cmd = str(str(command.split(": ", 1)[1]).split(" ", 1)[0])
				elif ':' in command:
					label = str(command.split(":", 1)[0])
					cmd = str(str(command.split(":", 1)[1]).split(" ", 1)[0])
				else:
					cmd = str(command.split(" ", 1)[0])

				if cmd == 'J':
					var1 = str(command.split(" ", 1)[1])
				else:
					var1 = str(re.split(', ', command.split(" ", 1)[1])[0].split("R", 1)[1])
					if int(var1) < 0 or int(var1) > 31:
						error = True
						MipsProgram.objects.all().delete()
						break;

					if cmd == "LD" or cmd == "SD":
						var2 = str(re.split(', |\(|\)', command.split(" ", 1)[1])[1])
						var3 = str(re.split(', |\(|\)', command.split(" ", 1)[1])[2].split("R", 1)[1])

					elif cmd == 'BEQC':
						var2 = str(re.split(', ', command.split(" ", 1)[1])[1].split("R", 1)[1])
						var3 = str(re.split(', ', command.split(" ", 1)[1])[2])

					else:
						var2 = str(re.split(', ', command.split(" ", 1)[1])[1].split("R", 1)[1])
						var3 = str(re.split(r'R|#', re.split(', ', command.split(" ", 1)[1])[2])[1])

				if cmd == "LD":
					output.append('110111'+ format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0], 16), '04b') + format(int(var2[1], 16), '04b') + format(int(var2[2], 16), '04b') + format(int(var2[3], 16), '04b'))

				elif cmd == "SD":
					output.append('111111' + format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0], 16), '04b') + format(int(var2[1], 16), '04b') + format(int(var2[2], 16), '04b') + format(int(var2[3], 16), '04b'))

				elif cmd == "DADDIU":
					output.append('011001' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0], 16), '04b') + format(int(var3[1], 16), '04b') + format(int(var3[2], 16), '04b') + format(int(var3[3], 16), '04b'))

				elif cmd == "XORI":
					output.append('001110' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0], 16), '04b') + format(int(var3[1], 16), '04b') + format(int(var3[2], 16), '04b') + format(int(var3[3], 16), '04b'))

				elif cmd == "DADDU":
					output.append('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101101')

				elif cmd == "SLT":
					output.append('000000' + format(int(var2), '05b') + format(int(var3), '05b') + format(int(var1), '05b') + '00000101010')

				elif cmd == 'BEQC':
					for index2, cmd2 in enumerate(cmdarr[index:]):
						if ':' in cmd2:
							label2 = str(cmd2.split(":", 1)[0])
							if label2 == var3:
								output.append('001000' + format(int(var1), '05b') + format(int(var2), '05b') + format(int(index2-1), '016b'))
				
				elif cmd == 'J':
					for index2, cmd2 in enumerate(cmdarr):
						if ':' in cmd2:
							label2 = str(cmd2.split(":", 1)[0])
							if label2 == var1:
								output.append('000010' + format(int(index2), '026b'))

				else:
					error = True
					MipsProgram.objects.all().delete()
					break;

				if not label == '':
					if cmd == "LD" or cmd == "DADDIU" or cmd == "XORI" or cmd == "SLT" or cmd == "DADDU":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), label=label, instruction=command, cmd=cmd, dest=var1, src1=var2, src2=var3)
					elif cmd == "SD":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), label=label, instruction=command, cmd=cmd, dest=var2, src1=var1, src2=var3)
					elif cmd == "BEQC":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), label=label, instruction=command, cmd=cmd, src1=var1, src2=var2, jumpTo=var3)
					elif cmd == "J":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), label=label, instruction=command, cmd=cmd, jumpTo=var1)
				else:
					if cmd == "LD" or cmd == "DADDIU" or cmd == "XORI" or cmd == "SLT" or cmd == "DADDU":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command, cmd=cmd, dest=var1, src1=var2, src2=var3)
					elif cmd == "SD":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command, cmd=cmd, dest=var2, src1=var1, src2=var3)
					elif cmd == "BEQC":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command, cmd=cmd, src1=var1, src2=var2, jumpTo=var3)
					elif cmd == "J":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command, cmd=cmd, jumpTo=var1)

				hexoutput.append(str(format(int(output[-1], 2), '08x')).upper())

				i += 1

			

			progObjects = MipsProgram.objects.all()
# START OF INTERNAL REGISTER
			lastProg = MipsProgram.objects.get(id=progObjects.count()-1)
			if lastProg.cmd == 'LD':
				address = format(int(int(lastProg.src1, 16) + int(int(Register.objects.get(id=int(lastProg.src2)).value, 16)/8)*8), '04x')
				reg = 'R' + str(lastProg.dest)
				wb = DataSegment.objects.get(addr=address).value
			elif lastProg.cmd == 'SD' or lastProg.cmd == 'BEQC' or lastProg.cmd == 'J':
				reg = ''
				wb = 'N/A'
			elif lastProg.cmd == 'DADDIU':
				immediate = int(Register.objects.get(id=int(lastProg.src1)).value, 16) + int(format(int(str(lastProg.src2)[0], 16), '04b') + format(int(str(lastProg.src2)[1], 16), '04b') + format(int(str(lastProg.src2)[2], 16), '04b') + format(int(str(lastProg.src2)[3], 16), '04b'), 2)
				hexcode = format(immediate, '04x').upper()

				if (binascii.unhexlify(hexcode))[0] == '1':
					wb = str("FFFFFFFFFFFF" + hexcode)
				else:
					wb = str('000000000000' + hexcode)
				reg = 'R' + str(lastProg.dest)
				print(wb)
			elif lastProg.cmd == 'XORI':
				immediate = format(int(str(lastProg.src2)[0], 16), '04b') + format(int(str(lastProg.src2)[1], 16), '04b') + format(int(str(lastProg.src2)[2], 16), '04b') + format(int(str(lastProg.src2)[3], 16), '04b')
				val = format(int(Register.objects.get(id=int(lastProg.src1)).value, 16), '016b')
				binary = ''
				for count in range(len(immediate)):
					if immediate[count] != val[count]:
						binary += '1'
					else:
						binary += '0'

				reg = 'R' + str(lastProg.dest)
				wb = format(int(binary, 2), '016x').upper()
				print(wb)
			elif lastProg.cmd == 'DADDU':
				operation = int(Register.objects.get(id=int(lastProg.src1)).value, 16) + int(Register.objects.get(id=int(lastProg.src2)).value, 16)
				reg = 'R' + str(lastProg.dest)
				wb = format(operation, '016x')
				print(wb)
			elif lastProg.cmd == 'SLT':
				operation = int(Register.objects.get(id=int(lastProg.src1)).value, 16) < int(Register.objects.get(id=int(lastProg.src2)).value, 16)
				if operation:
					wb = format(int(Register.objects.get(id=int(lastProg.src1)).value, 16), '016x')
					reg = 'R' + str(lastProg.dest)
				else:
					wb = ''
					reg = ''

			for program in progObjects:
				if program.cmd == 'LD':
					address = format(int(int(program.src1, 16) + int(int(Register.objects.get(id=int(program.src2)).value, 16)/8)*8), '04x')
					wback = DataSegment.objects.get(addr=address).value
					regObj = Register.objects.get(id=int(program.dest))
					regObj.value = wback
					regObj.save()
				elif program.cmd == 'SD':
					address = format(int(int(program.dest, 16) + int(int(Register.objects.get(id=int(program.src2)).value, 16)/8)*8), '04x')
					print(address)
					wback = Register.objects.get(id=int(program.src1)).value
					memObj = DataSegment.objects.get(addr=str(address))
					memObj.value = wback
					memObj.save()

				elif program.cmd == 'BEQC' or program.cmd == 'J':
					wback = 'N/A'
				elif program.cmd == 'DADDIU':
					immediate = int(Register.objects.get(id=int(program.src1)).value, 16) + int(format(int(str(program.src2)[0], 16), '04b') + format(int(str(program.src2)[1], 16), '04b') + format(int(str(program.src2)[2], 16), '04b') + format(int(str(program.src2)[3], 16), '04b'), 2)
					hexcode = format(immediate, '04x').upper()
					print("DADDIU")
					if (binascii.unhexlify(hexcode))[0] == '1':
						wback = str("FFFFFFFFFFFF" + hexcode)
					else:
						wback = str('000000000000' + hexcode)
					regObj = Register.objects.get(id=int(program.dest))
					regObj.value = wback
					regObj.save()
				elif program.cmd == 'XORI':
					immediate = str(format(int(str(program.src2)[0], 16), '04b') + format(int(str(program.src2)[1], 16), '04b') + format(int(str(program.src2)[2], 16), '04b') + format(int(str(program.src2)[3], 16), '04b'))
					val = str(format(int(Register.objects.get(id=int(program.src1)).value, 16), '016b'))
					print(immediate)
					print(val)
					binary = ''
					for count in range(len(immediate)):
						if immediate[count] != val[count]:
							binary += '1'
						else:
							binary += '0'
					wback = format(int(binary, 2), '016x').upper()
					print(binary)
					regObj = Register.objects.get(id=int(program.dest))
					regObj.value = wback
					regObj.save()
				elif program.cmd == 'DADDU':
					operation = int(Register.objects.get(id=int(program.src1)).value, 16) + int(Register.objects.get(id=int(program.src2)).value, 16)
					wback = format(operation, '016x')
					print("DADDU")
					regObj = Register.objects.get(id=int(program.dest))
					regObj.value = wback
					regObj.save()

				elif program.cmd == 'SLT':
					operation = int(Register.objects.get(id=int(program.src1)).value, 16) < int(Register.objects.get(id=int(program.src2)).value, 16)
					if operation:
						wback = format(int(Register.objects.get(id=int(program.src1)).value, 16), '016x')
						regObj = Register.objects.get(id=int(program.dest))
						regObj.value = wback
						regObj.save()

			progObjects = MipsProgram.objects.all()
			lengthOfLast = 0
			jumpLocation = ''
			lastCmd = -1
			allocate = 2
			btrigger = False
			jtrigger = False
			foundj = False

			for i in range(progObjects.count()):
				temp = []
				dependent = -1

				if i == 0:
					pipeline.append(['IF', 'ID', 'EX', 'MEM', 'WB'])
				else:
					if btrigger or jtrigger:
						if jumpLocation == MipsProgram.objects.get(id=i).label:
							jumpLocation = ''
							for j in range(pipeline[lastCmd].index("ID")):
								temp.append(" ")

							lastCmd = -1
							temp.append("IF")
							temp.append('ID')
							temp.append('EX')
							temp.append('MEM')
							temp.append('WB')
							pipeline.append(temp)
							jtrigger = False
							btrigger = False
							allocate = 2

						else:
							temp.append(" ")
							pipeline.append(temp)
					else:

						for j in range(pipeline[i-1].index("ID")):
							temp.append(" ")
						temp.append("IF")
						for k in range(progObjects.count() - 1):
							if not ((MipsProgram.objects.get(id=i).src1 == '' and MipsProgram.objects.get(id=i).src2 == '') or MipsProgram.objects.get(id=k).dest == ''):
								if MipsProgram.objects.get(id=k).dest == MipsProgram.objects.get(id=i).src1 or MipsProgram.objects.get(id=k).dest == MipsProgram.objects.get(id=i).src2:
									dependent = k
						if not dependent == -1:	
							while pipeline[dependent].index("WB") > len(temp):
								temp.append("*")
						
						if MipsProgram.objects.get(id=i-1).cmd == 'BEQC' and Register.objects.get(id=int(MipsProgram.objects.get(id=i-1).src1)).value == Register.objects.get(id=int(MipsProgram.objects.get(id=i-1).src2)).value:
							if temp[len(temp)-1] == 'IF':
								temp.append('ID')
								temp.append('EX')
								pipeline.append(temp)
								lastCmd = i
								btrigger = True
								jumpLocation = MipsProgram.objects.get(id=i-1).jumpTo

							elif temp[len(temp)-1] == '*':
								temp.append('ID')
								pipeline.append(temp)
								lastCmd = i
								btrigger = True
								jumpLocation = MipsProgram.objects.get(id=i-1).jumpTo

						elif MipsProgram.objects.get(id=i).cmd == 'J':
							foundj = True
							jumpLocation = MipsProgram.objects.get(id=i).jumpTo
							temp.append('ID')
							temp.append('EX')
							temp.append('MEM')
							temp.append('WB')
							pipeline.append(temp)

						else:
							temp.append('ID')
							temp.append('EX')
							temp.append('MEM')
							temp.append('WB')
							pipeline.append(temp)
							if foundj and allocate > 0:
								allocate -= 1
							elif allocate == 0:
								foundj = False
								lastCmd = i
								jtrigger = True
				lengthOfLast = len(temp)

			context = {
				'reg': reg,
				'wb': wb,
				'progObjects': progObjects,
				'objectCount': progObjects.count(),
				'error': error,
				'cmdarr': cmdarr,
				'pipeline': pipeline,
				'pipLast': range(1, lengthOfLast + 1),
			}
			return render(request, 'processor/index.html', context)
			
		except:
			error = True
			MipsProgram.objects.all().delete()

			context = {
				'progObjects': progObjects,
				'objectCount': progObjects.count(),
				'error': error,
				'cmdarr': cmdarr,
				'pipeline': pipeline,
				'pipLast': range(1, len(pipeline[-1]) + 1),
			}

			return render(request, 'processor/index.html', context)
	
	context = {
		'progObjects': progObjects,
		'objectCount': progObjects.count(),
		'error': error,
	}

	return render(request, 'processor/index.html', context)

def regInput(request):
	if request.method == 'POST':
		regnum = request.POST['regNum']
		regval = request.POST['regVal']
		leading = ''
		if len(regval) < 16:
			for i in range(16-len(regval)):
				leading += '0'

			regval = leading + regval

		regObject = Register.objects.filter(id=regnum).get()
		regObject.value = regval
		regObject.save()

	reg = Register.objects.all()

	context = {
		'reg': reg,
	}

	return render(request, 'processor/reginput.html', context)

def memInput(request):
	if request.method == 'POST':
		memaddr = request.POST['memAddr']
		memval = request.POST['memVal']
		leading = ''
		if len(memval) < 16:
			for i in range(16-len(memval)):
				leading += '0'

			memval = leading + memval

		memObject = DataSegment.objects.filter(addr=memaddr).get()
		memObject.value = memval
		memObject.save()

	mem = DataSegment.objects.all()

	context = {
		'mem': mem,
	}

	return render(request, 'processor/meminput.html', context)

def initialize(request):
	regObjects = Register.objects.all()
	dataObjects = DataSegment.objects.all()
	programObjects = MipsProgram.objects.all()
	address = 0

	if regObjects.count() == 0:
		for i in range(32):
			Register.objects.create(id=i)
	else:
		for reg in regObjects:
			reg.value = '0000000000000000'
			reg.save()

	if dataObjects.count() == 0:
		for i in range(512):
			DataSegment.objects.create(id=i, addr=str(format(address, '04x')).upper())
			address += 8
	else:
		for data in dataObjects:
			data.value = '0000000000000000'
			data.save()

	if programObjects.count() > 0:
		MipsProgram.objects.all().delete()

	return redirect('/')
