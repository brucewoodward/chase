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


class CurrentChart:
    def __init__(self):
        self.charts = {}
        self.current = None

    def get(self, name):
        if self.charts.has_key(name):
            return self.charts[name]
        else:
            return None
        
    def get_current(self):
        if self.current:
            return self.charts[self.current] # returns the ds object
        else:
            return None
        
    def add(self, name, chart): # chart is actually the dataseries
        self.charts[name] = chart
        
    def set_current(self, name):
        if self.charts.has_key(name):
            self.current = name
        else:
            raise "No such chart"
        
    def delete_current(self):
        c = self.get_current()
        if c != None:
            del self.charts[self.current]
            charts= self.charts.keys()
            charts.sort()
            if len(charts) != 0:
                self.set_current(charts[0])
                return charts[0]
            else:
                self.current = None

    def get_all(self):
        return self.charts.keys()

    def get_current_name(self):
        return self.current
