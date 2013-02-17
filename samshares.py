#!/usr/bin/python

# SamShares
# This will pull financial data out of Annual Report PDFs
# I plan to update PyPDF2 to suit my needs here

import re

import sys
import os.path
from copy import copy
# this will let me import from PyPDF2
sys.path.append(os.path.dirname(__file__) + "/../PyPDF2")
import PyPDF2


# I want to extract the text in a form that I can manupulate
# Apparently pdf.getPage(i) gets me a PageObject
# we can use this to extract more stuff somehow...
#
# PageObject subclasses DictionaryObject
# DictionaryObject.arr is a dictionary with stuff in it
# tempted to just JSONprint it...
#
# Let's look through PageObject.extractText() and get something
# useful out of it
#
# Wrapped it, text objects are char at a time, looking a bit deeper:
# pdf.py has _decryptobject(), see if this stores co-ordinates

f = open('pdfdetails.txt', 'r')
line = f.readline()
(filename, num) = line.split(':')
pdf = PyPDF2.PdfFileReader(file(filename, 'rb'))
page = pdf.getPage(int(num))
# get array of TextStringObject
tso = page.getTextObjects()
# print and see what happens

for bit in tso:
  print ("Object: %(bit)s" % locals()).encode('ascii',errors='backslashreplace')

#print page.extractText().encode('ascii',errors='backslashreplace')

#print "\n\n\n"

#page = pdf2.getPage(3)
#print page.extractText().encode('ascii',errors='backslashreplace')
