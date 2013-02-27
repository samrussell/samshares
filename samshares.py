#!/usr/bin/python

# SamShares
# This will pull financial data out of Annual Report PDFs
# I plan to update PyPDF2 to suit my needs here

import re
import pprint
from numpy import matrix
import copy

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

content = page["/Contents"].getObject()
if not isinstance(content, PyPDF2.pdf.ContentStream):
    content = PyPDF2.pdf.ContentStream(content, page.pdf)

#baselocation = [0,0]
#location = [0,0]

# text stuff SUCKS
# so here's the deal:
# we have two matrices - the text matrix, and the line matrix
# the line matrix is where we fall back to on new-line commands
# the text matrix is where text is currently rendered to
#
# the units used are "text units" - 1/72 x 1/72 inch
# the "point" used for fonts is a multiple of this
# so 12-point font should be scaled 12 times - a "standard glyph"
# should be 1/6 x 1/6 inches big
# IMPORTANT - the positioning is not related to the font
# but we need this to find out how wide the words are
#
# Affine transforms are done with 1x3 instead of 3x1 matrices for the
# co-ordinates, so (x,y) is represented as [x,y,1], multiplied by
# the text matrix (from the left: coords * tm), giving the coords as
# [x', y', 1]

identity3_3 = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
initialcoord1_3 = matrix([[1,1,1]])
textmatrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
textlinematrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
leadingparameter = 0

# make framestrings look like this:
# [
#   ['string1', x1, y1],
#   ['string2', x2, y2],
# ]

framestrings = []

for operands,operator in content.operations:
  # let's find out how the Tj TJ T* operators work...
  if operator=='Tj':
    bigstring = ''.join(operands)
    coords = initialcoord1_3 * textmatrix
    # add to framestrings
    framestrings.append([bigstring, coords.item(0), coords.item(1)])
    # increase location[0] by length of string
    toprint = "String (%d, %d) \"%s\" <%s>" % (coords.item(0), coords.item(1), unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
    print "(%d,%d) %s" % (coords.item(0), coords.item(1), unicode(bigstring).encode('ascii',errors='backslashreplace'))
    addwidth = matrix([[0,0,0], [0,0,0], [len(bigstring)*16,0,0]])
    textmatrix += addwidth
  elif operator=='TJ':
    # pattern is char spacing char spacing
    # ignore spacing
    #pprint.pprint(operands)
    bigstring = ''.join(operands[0][::2])
    coords = initialcoord1_3 * textmatrix
    # add to framestrings
    framestrings.append([bigstring, coords.item(0), coords.item(1)])
    # increase location[0] by length of string
    #bigstring = ''.join(operands[::2])
    toprint = "String (%d, %d) \"%s\" <%s>" % (coords.item(0), coords.item(1), unicode(bigstring).encode('ascii',errors='backslashreplace'), operator)
    print "(%d,%d) %s" % (coords.item(0), coords.item(1), unicode(bigstring).encode('ascii',errors='backslashreplace'))
    addwidth = matrix([[0,0,0], [0,0,0], [len(bigstring)*16,0,0]])
    textmatrix += addwidth
  elif operator=='BT':
    # reset location
    textmatrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    textlinematrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    toprint = "Begin text"
  elif operator=='ET':
    toprint = "End text"
  elif operator=='Tm':
    # 6 fields in array
    # x = a*x + c*y + e
    # x = b*x + d*y + f
    #newlocation = []
    #newlocation.append(location[0]*operands[0] + location[1]*operands[2] + operands[4])
    #newlocation.append(location[0]*operands[1] + location[1]*operands[3] + operands[5])
    # cheat and just use operands[4] and operands[5]
    #newlocation = [operands[4], operands[5]*2]
    #baselocation[0] = newlocation[0]
    #baselocation[1] = newlocation[1]
    textmatrix = matrix([[operands[0], operands[1], 0], [operands[2], operands[3], 0], [operands[4], operands[5], 1]])
    textlinematrix = matrix([[operands[0], operands[1], 0], [operands[2], operands[3], 0], [operands[4], operands[5], 1]])
    #location = newlocation
    coords = initialcoord1_3 * textmatrix
    toprint = "New location: (%d, %d) <%s>" % (coords.item(0), coords.item(1), operator)
  elif operator=='Td':
    # cheat
    #baselocation[0] += operands[0]*12
    #baselocation[1] += operands[1]
    #location[0] = baselocation[0]
    #location[1] = baselocation[1]
    translationmatrix = matrix([[1, 0, 0], [0, 1, 0], [operands[0], operands[1], 1]])
    textlinematrix = translationmatrix * textlinematrix
    textmatrix = identity3_3 * textlinematrix
    toprint = "New location %d %d: <%s>" % (coords.item(0), coords.item(1), operator)
  elif operator=='TD':
    # cheat
    # should set line operator (TL -operands[1])
    #baselocation[0] += operands[0]*12
    #baselocation[1] += operands[1]
    #location[0] = baselocation[0]
    #location[1] = baselocation[1]
    translationmatrix = matrix([[1, 0, 0], [0, 1, 0], [operands[0], operands[1], 1]])
    textlinematrix = translationmatrix * textlinematrix
    textmatrix = identity3_3 * textlinematrix
    toprint = "New location %d %d: <%s>" % (coords.item(0), coords.item(1), operator)
  elif operator=='T*':
    addheight = matrix([[0,0,0], [0,0,0], [0,24,0]])
    textlinematrix += addheight
    textmatrix = translationmatrix * textlinematrix
  # need to still do Tc, Tw, Td
  # Td = move to next line with stuff (5.3.1)
  # Tc = charSpace, Tw = wordSpace (5.2.1)
  else:
    toprint = "%s <%s>" % (unicode(operands).encode('ascii',errors='backslashreplace'), operator)
  #print toprint
  #print unicode(operands).encode('ascii',errors='backslashreplace'),
  #print ("<%s>" % operator)

#print page.extractText().encode('ascii',errors='backslashreplace')

#print "\n\n\n"

#page = pdf2.getPage(3)
#print page.extractText().encode('ascii',errors='backslashreplace')

# create a window to draw where text should go on the page

import wx

class Frame(wx.Frame):
  def __init__(self, title, framestrings):
    wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(800,800))
    
    panel = wx.Panel(self, -1)
    font = wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL)
    for fs in framestrings:
      #textout = wx.StaticText(panel, -1, fs[0],(fs[1], fs[2]*-1 + 800), style=wx.ALIGN_CENTRE)
      textout = wx.StaticText(panel, -1, "X",(fs[1], fs[2]*-1 + 800), style=wx.ALIGN_CENTRE)

app = wx.App()

frame = Frame('test frame', framestrings)
frame.Show()

app.MainLoop()

#pprint.pprint(framestrings)

