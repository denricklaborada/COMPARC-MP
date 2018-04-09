from __future__ import unicode_literals
from django.shortcuts import render, redirect
import re
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

				if ':' in command:
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
					output.append('111111' + format(int(var3), '05b') + format(int(var1), '05b') + format(int(var2[0]), '04b') + format(int(var2[1]), '04b') + format(int(var2[2]), '04b') + format(int(var2[3]), '04b'))

				elif cmd == "DADDIU":
					output.append('011001' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

				elif cmd == "XORI":
					output.append('001110' + format(int(var2), '05b') + format(int(var1), '05b') + format(int(var3[0]), '04b') + format(int(var3[1]), '04b') + format(int(var3[2]), '04b') + format(int(var3[3]), '04b'))

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
					if cmd == "LD" or cmd == "DADDIU" or cmd == "XORI" or cmd == "SLT":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), label=label, instruction=command, cmd=cmd, dest=var1, src1=var2, src2=var3)
				else:
					if cmd == "LD" or cmd == "DADDIU" or cmd == "XORI" or cmd == "SLT":
						MipsProgram.objects.create(id=i, addr='1' + str(format((len(output) - 1) * 4, '03x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command, cmd=cmd, dest=var1, src1=var2, src2=var3)

				hexoutput.append(str(format(int(output[-1], 2), '08x')).upper())

				i += 1

			progObjects = MipsProgram.objects.all()

			for i in range(progObjects.count()):
				temp = []
				dependent = -1

				if i == 0:
					pipeline.append(['IF', 'ID', 'EX', 'MEM', 'WB'])
				else:
					for j in range(pipeline[i-1].index("ID")):
						temp.append(" ")
					temp.append("IF")
					for k in range(progObjects.count() - 1):
						if MipsProgram.objects.get(id=k).dest == MipsProgram.objects.get(id=i).src1 or MipsProgram.objects.get(id=k).dest == MipsProgram.objects.get(id=i).src2:
							dependent = k
					if not dependent == -1:	
						while pipeline[dependent].index("WB") > len(temp):
							temp.append("*")
								
					temp.append('ID')
					temp.append('EX')
					temp.append('MEM')
					temp.append('WB')
					pipeline.append(temp)

			context = {
				'progObjects': progObjects,
				'error': error,
				'cmdarr': cmdarr,
				'pipeline': pipeline,
				'pipLast': range(1, len(pipeline[-1]) + 1),
			}
			return render(request, 'processor/index.html', context)
			
		except:
			error = True
			MipsProgram.objects.all().delete()

			context = {
				'progObjects': progObjects,
				'error': error,
				'cmdarr': cmdarr,
				'pipeline': pipeline,
				'pipLast': range(1, len(pipeline[-1]) + 1),
			}

			return render(request, 'processor/index.html', context)
	
	context = {
		'progObjects': progObjects,
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

		return redirect('/')

	return render(request, 'processor/reginput.html')

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

		return redirect('/')

	return render(request, 'processor/meminput.html')

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
