#!/usr/bin/python

# findlines.py
# This will take test output from samshares.py and attempt to find lines
# that would represent rows and columns

import re
import wx
import sys

class Frame(wx.Frame):
  def __init__(self, title):
    wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(800,800))
    
    panel = wx.Panel(self, -1)
    font = wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL)
    
    # First parse the file

    f = open('testoutput6.txt', 'r')

    # Read in all lines in format (x,y) string
    # Save these as arrays and store in a dictionary

    rows = {}
    cols = {}

    for line in f:
      # parse details
      m = re.match(r"\(\s*([0-9]+)\s*,\s*([0-9]+)\s*\)\s*(.+)", line)
      if m:
        x = int(m.group(1))
        y = int(m.group(2))
        text = m.group(3)
        # store in rows and cols
        # rows is rows[row[col[text]]
        # cols is cols[col[row[text]]
        if x/6 not in cols:
          cols[(x/6)] = {}
        cols[(x/6)][(y/6)] = text
        if y/6 not in rows:
          rows[(y/6)] = {}
        rows[(y/6)][(x/6)] = text
        textout = wx.StaticText(panel, -1, text,(x, y*-1 + 800), style=wx.ALIGN_CENTRE)

    # Now scan through each row and see if we can find lines in each column
    # count as a line if we get more than 6 things in there
    
    for x in cols.keys():
      colrows = cols[x].keys()
      if len(colrows) > 6:
        # draw between the first and last chars
        low = min(colrows)*6
        high = max(colrows)*6
        length = high-low
        line = wx.StaticLine(panel, -1, wx.Point(x*6,(high*-1)+800), wx.Size(3,length),wx.LI_VERTICAL)
        line.SetForegroundColour(wx.Colour(0,255,0))
        
    # Do some tests for rows
    
    for y in rows.keys():
      rowcols = rows[y].keys()
      if len(rowcols) > 2:
        # draw between the first and last chars
        low = min(rowcols)*6
        high = max(rowcols)*6
        length = high-low
        line = wx.StaticLine(panel, -1, wx.Point(low,(y*6*-1)+800), wx.Size(length,3),wx.LI_HORIZONTAL)
        line.SetForegroundColour(wx.Colour(0,255,0))

app = wx.App(redirect=False)

frame = Frame('test frame')
frame.Show()

app.MainLoop()

