# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class GPRegister(models.Model):
	regNum = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(31)])
	representation = models.CharField(default="0000000000000000", max_length=16)

class FPRegister(models.Model):
	regNum = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(31)])
	representation = models.CharField(default="0000000000000000", max_length=16)

class DataSegment(models.Model):
	addr = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4095)])
	representation = models.CharField(default="0000000000000000", max_length=16)
	instruction = models.CharField(blank=True, max_length=30)

class CommandAddress(models.Model):
	addr = models.PositiveIntegerField(default=0, validators=[MinValueValidator(4096), MaxValueValidator(8191)])
	opcode = models.CharField(blank=True, max_length=8)
	