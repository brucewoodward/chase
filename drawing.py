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

import gtk

_vals = {}

# do setup.
_vals['win'] = None
_vals['drawline_func'] = None
_vals['drawrectangle_func'] = None
_vals['drawtext_func'] = None
_vals['drawpoints_func'] = None

def set_window(win):
    _vals['win'] = win
def get_window():
    return _vals['win']

def get_drawline_func():
    return _vals['drawline_func']
def set_drawline_func(func):
    _vals['drawline_func'] = func

def get_drawrectangle_func():
    return _vals['drawrectangle_func']
def set_drawrectangle_func(func):
    _vals['drawrectangle_func'] = func

def get_drawtext_func():
    return _vals['drawtext_func']
def set_drawtext_func(func):
    _vals['drawtext_func'] = func

def get_drawpoints_func():
    return _vals['drawpoints_func']
def set_drawpoints_func(func):
    _vals['drawpoints_func'] = func

def set_primary_pixmap(p):
    _vals['ppixmap'] = p
def get_primary_pixmap():
    return _vals['ppixmap']

def set_secondary_pixmap(p):
    _vals['spixmap'] = p
def get_secondary_pixmap():
    return _vals['spixmap']

class colour:
    def __init__(self, colour=None):
        self.colour = colour
        self.allocd_colour = colour
        self.gc = None
        if colour != None:
            self.set_colour(colour)
            
    def set_colour(self, colour):
        w = get_window() # check if a window has been setup yet.
        if w == None:
            raise "Window not set"
        self.colour = colour
        self.alloced_colour = w.get_window().colormap.alloc(colour)
        gc = _vals['win'].get_window().new_gc()
        gc.foreground = self.alloced_colour
        self.gc = gc
        return 1
        
    def get_colour(self):
        return self.gc

    def get_colour_name(self):
        return self.colour

def drawline(colour, x1, y1, x2, y2):
    df = _vals['drawline_func']
    if df == None:
        raise "Draw Line Function not set"
    df(get_primary_pixmap(), colour.get_colour(), x1, y1, x2, y2)
    df(get_secondary_pixmap(), colour.get_colour(), x1, y1, x2, y2)

def drawrectangle(colour, x1, y1, x2, y2, fill):
    dr = _vals['drawrectangle_func']
    if dr == None:
        raise "Draw Rectnagle Function not set"
    dr(get_primary_pixmap(), colour.get_colour(), fill, x1, y1, x2, y2)
    dr(get_secondary_pixmap(), colour.get_colour(), fill, x1, y1, x2, y2)
    
def drawtext(font, colour, x, y, string):
    dt = _vals['drawtext_func']
    if dt == None:
        raise "Draw Text Function not set"
    dt(get_primary_pixmap(), font.get_font(),
       colour.get_colour(), x, y, string)
    dt(get_secondary_pixmap(), font.get_font(),
       colour.get_colour(), x, y, string)
    
def drawpoints(colour, points):
    dp = _vals['drawpoints_func']
    if dp == None:
        raise "Draw Points Function not set"
    dp(get_primary_pixmap(), colour.get_colour(), points)
    dp(get_secondary_pixmap(), colour.get_colour(), points)

def drawtext_onsec(font, colour, x, y, string):
    dt = _vals['drawtext_func']
    if dt == None:
        raise "Draw Text Function not set"
    dt(get_secondary_pixmap(), font.get_font(),
       colour.get_colour(), x, y, string)

class font:
    def __init__(self, name=None):
        self.font_name = name
        self.font = None
        if self.font_name != None:
            self.set_font(name)

    def set_font(self, name):
        self.font = gtk.load_font(name)
        return self.font

    def get_font(self):
        return self.font

# the following functions are to simplify the drawing of a drawable.
# all information is setup in the Chart.draw method and is always valid.
#
# drawables can query these values but should never change them.
#
# The functions/information here is what is calculated by the chart.
# Subcharts can do their own thing.

def set_xscale(xscale):
    _vals['xscale'] = xscale
def get_xscale():
    return _vals['xscale']

def set_yscale(yscale):
    _vals['yscale'] = yscale
def get_xscale():
    return _vals['yscale']

def set_start_bar(sbar):
    _vals['start_bar'] = sbar
def get_start_bar():
    return _vals['start_bar']

def set_numbars(nbar):
    _vals['numbars'] = nbar
def get_numbars():
    return _vals['numbars']

