#!/usr/bin/env python
#    chase 
#    Copyright (C) 2003 Bruce Woodward

#    chase is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    chase is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with chase; see the file COPYING. If not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import sys
import math

def round(v):
    rt = 0.0
    (frac, num) = math.modf(v)
    #num = int(num)
    #print "frac: ", frac, " num: ", num
    if frac >= 0.5:
        rt = float(num) + 1.0
    else:
        rt = int(num)
    #print "rt: ", rt
    return int(rt)
    #return int(v)


def is_eq(a, b):
    """ is equal to 2 decimal places """
    diff = abs(a - b)
    if diff < 0.009:
        return 1
    else:
        return 0


def is_le(a, b):
    """ is less than or equal too, to 2 decimal places """
    diff = a - b
    if is_eq(a, b):
        return 1
    if a < b and abs(a - b) > 0.009:
        return 1
    return 0

def split_date_string(strdate):
    currentdate = str(strdate)
    year = int(currentdate[:4])
    month = int(currentdate[4:6])
    day = int(currentdate[6:8])
    return year, month, day


def endOfWeek(dayOfMonth, dayOfWeek):
    return dayOfMonth + dayOfWeek + 1

if __name__ == '__main__':
    import unittest

    class test(unittest.TestCase):

        def testEndOfWeek(self):
            for d in range(1,6):
                eow= endOfWeek(6, d)
