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


class DataSet:
    def __init__(self, Header=None, Series=None):
        self.vals = {}
        if Header:
            register(self, Header, Series)
     
    def register(self, Header, Series):
        """ Header - title of the dataseries (string)
        Series - list of numbers.
        """
        self.vals[Header] = Series
        if Header == 'date':
            self.__hash_date(Series)
        return self

    def __hash_date(self, Series):
        hash = self.vals['date-hash'] = {}
        for i in xrange(0, len(Series)):
            hash[str(Series[i])] = i

    
    def get(self, Header):
        """ Return list of values associated with Header.
        Raise exception if header doesn't exist.
        """
        if self.vals.has_key(Header):
            return self.vals[Header]
        else:
            raise "Header doesn't exist", Header
        
    def delete(self, Header):
        """ Delete Header from the DataSet
        Raise exception is Header doesn't exist
        """
        if self.vals.has_key(Header):
            del(self.vals[Header])
        else:
            raise "Header doesn't exist", Header

    def get_headers(self):
        """ Return a list of the Headers.
        """
        return self.vals.keys()

    def replace(self, header, array):
        if self.vals.has_key(header):
            del self.vals[header]
            self.register(header, array)

#INVALID_YEAR = -1
#INVALID_MONTH = -2
#INVALID_DAY = -3

#def is_date_valid(date):
#    count = 0
#    for x in date:
#        count += count
#        d = str(x)
#        year = d[:4]
#        month = d[4:6]
#        day = d[6:]
#        if year < 1700:
#            return (INVALID_YEAR, count)
#        if month < 1 or month > 12:
#            return (INVALID_MONTH, count)
#        if day < 1 or day > 31:
#            return (INVALID_DAY, count) # XXXX should code this up correctly
#    return 1
    
