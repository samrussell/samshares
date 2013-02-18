#!/usr/bin/python

# SamShares
# This will pull financial data out of Annual Report PDFs
# I plan to update PyPDF2 to suit my needs here

import re
import pprint

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


f = open('pdfdetails.txt', 'r')
line = f.readline()
(filename, num) = line.split(':')
pdf = PyPDF2.PdfFileReader(file(filename, 'rb'))
page = pdf.getPage(int(num))

# Let's write functions to parse Tj and TJ

def parsePDFLine(operator, operands, location):
  if operator=='Tj':
    bigstring = ''.join(operands)
    toreturn = "String \"%s\" <%s>" % (unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
  elif operator=='TJ':
    # pattern is char spacing char spacing
    # ignore spacing
    #pprint.pprint(operands)
    bigstring = ''.join(operands[0][::2])
    #bigstring = ''.join(operands[::2])
    toreturn = "String (%d, %d)  \"%s\" <%s>" % (location[0], location[1], unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
  elif operator=='BT':
    # reset location
    baselocation = [0,0]
    location = [0,0]
    toreturn = "Begin text"
  elif operator=='ET':
    toreturn = "End text"
  elif operator=='Tm':
    # 6 fields in array
    # x = a*x + c*y + e
    # x = b*x + d*y + f
    newlocation = []
    newlocation.append(location[0]*operands[0] + location[1]*operands[2] + operands[4])
    newlocation.append(location[0]*operands[1] + location[1]*operands[3] + operands[5])
    location = newlocation
    toreturn = "New location: (%d, %d) <%s>" % (location[0], location[1], operator)
  else:
    toreturn = "%s <%s>" % (unicode(operands).encode('ascii',errors='backslashreplace'), operator)
  
  return (toreturn, location)

content = page["/Contents"].getObject()
if not isinstance(content, PyPDF2.pdf.ContentStream):
    content = PyPDF2.pdf.ContentStream(content, page.pdf)

baselocation = [0,0]
location = [0,0]

for operands,operator in content.operations:
  # let's find out how the Tj TJ T* operators work...
  if operator=='Tj':
    bigstring = ''.join(operands)
    toprint = "String (%d, %d) \"%s\" <%s>" % (location[0], location[1], unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
  elif operator=='TJ':
    # pattern is char spacing char spacing
    # ignore spacing
    #pprint.pprint(operands)
    bigstring = ''.join(operands[0][::2])
    #bigstring = ''.join(operands[::2])
    toprint = "String (%d, %d) \"%s\" <%s>" % (location[0], location[1], unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
  elif operator=='BT':
    # reset location
    baselocation = [0,0]
    location = [0,0]
    toprint = "Begin text"
  elif operator=='ET':
    toprint = "End text"
  elif operator=='Tm':
    # 6 fields in array
    # x = a*x + c*y + e
    # x = b*x + d*y + f
    newlocation = []
    newlocation.append(location[0]*operands[0] + location[1]*operands[2] + operands[4])
    newlocation.append(location[0]*operands[1] + location[1]*operands[3] + operands[5])
    baselocation = newlocation
    location = newlocation
    toprint = "New location: (%d, %d) <%s>" % (location[0], location[1], operator)
  # need to still do Tc, Tw, Td
  # Td = move to next line with stuff (5.3.1)
  # Tc = charSpace, Tw = wordSpace (5.2.1)
  elif operator=='Td':
    pass
  else:
    toprint = "%s <%s>" % (unicode(operands).encode('ascii',errors='backslashreplace'), operator)
  print toprint
  #print unicode(operands).encode('ascii',errors='backslashreplace'),
  #print ("<%s>" % operator)

#print page.extractText().encode('ascii',errors='backslashreplace')

#print "\n\n\n"

#page = pdf2.getPage(3)
#print page.extractText().encode('ascii',errors='backslashreplace')
