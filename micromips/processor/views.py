from __future__ import unicode_literals
from django.shortcuts import render, redirect
import re
from .models import Register, DataSegment, MipsProgram

def index(request):
	progObjects = MipsProgram.objects.all()

	if request.method == 'POST':
		try:
			commands = request.POST['commands']
			cmdarr = commands.splitlines()
			output = []
			hexoutput = []
			i = 0
			MipsProgram.objects.all().delete()
			for command in cmdarr:
				cmd = str(command.split(" ", 1)[0])
				var1 = str(re.split(', ', command.split(" ", 1)[1])[0].split("R", 1)[1])
				if int(var1) < 0 or int(var1) > 31:
					error = "Register out of bound"

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

				MipsProgram.objects.create(id=i, addr=str(format((len(output)-1)*4, '04x')).upper(), opcode=str(format(int(output[-1], 2), '08x')).upper(), instruction=command)

				hexoutput.append(str(format(int(output[-1], 2), '08x')).upper())

				i += 1

			progObjects = MipsProgram.objects.all()

			context = {
				'progObjects': progObjects,
				'error': error,
			}
			return render(request, 'processor/index.html', context)
			
		except:
			context = {
				'progObjects': progObjects,
			}

			return render(request, 'processor/index.html', context)
	
	context = {
		'progObjects': progObjects,
	}

	return render(request, 'processor/index.html', context)

def regInput(request):
	regObject = Register.objects.filter(id=1).get()
	regObject.value = 'FFFFFFFFFFFFFFFF'
	regObject.save()

	return redirect('/')

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
