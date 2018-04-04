# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Register(models.Model):
	value = models.CharField(default="0000000000000000", max_length=16)

	def __str__(self):
		return str(self.id)

class DataSegment(models.Model):
	addr = models.CharField(blank=True, max_length=4)
	value = models.CharField(default="0000000000000000", max_length=16)

	def __str__(self):
		return str(self.addr)

class MipsProgram(models.Model):
	addr = models.CharField(blank=True, max_length=4)
	opcode = models.CharField(blank=True, max_length=8)
	label = models.CharField(blank=True, max_length=20)
	instruction = models.CharField(blank=True, max_length=50)

	def __str__(self):
		return str(self.addr)
	