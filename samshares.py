#!/usr/bin/python

# SamShares
# This will pull financial data out of Annual Report PDFs
# I plan to update PyPDF2 to suit my needs here

import sys
import os.path
from copy import copy
# this will let me import anything out of the parent directory
sys.path.append(os.path.dirname(__file__) + "/..")

