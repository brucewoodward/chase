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

import os, re, array, sys
#from CurrentChart import *


def _strip_white_space(s): # expect a string as first arg
    r = []
    for x in s:
        x = x.lstrip()
        x = x.rstrip()
        r.append(x)
    return r

def load_data_file(dfile):
    """ Open dfile and parse contents.
    Returns an array of tuples. (Header, list of values)
    """
    p = open(dfile)
    lines = p.readlines()
    # remove trailing newline char.
    lines = map(lambda x: x[:-1], lines)
    # read the header
    i=0
    max = len(lines)
    header=''
    while i < max:
        if lines[i][0] == '#':
            continue
        else:
            header = lines[i]
            break
        i += 1
    # now we have the header line
    title = _strip_white_space(re.split(',', header))
    values = []
    for x in range(len(title)):
        ar = array.array('d')
        values.append(ar)
    i += 1    
    while i < max:
        v = lines[i].split(',');
        if len(v) != len(title):
            raise "Bad data", i
        for x in range(len(title)):
            f = float(v[x])
            try:
                values[x].append(f)
            except:
                print "i is %d and x is %d" % (i, x)
                sys.exit(1)
        i += 1
    # build up return structure
    dset = {}
    for x in range(len(title)):
        dset[title[x]] = values[x]
    return dset

