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


# YScale isn't a class, but has simpler interface than Chart, Subchart and
# Drawable.

# try and display every .25, then every .50, then every 1.00, then every
# 2.50, then every 5.00, then every etc ...
# boils down to trying the intial values of .25, .50 and 1.00 in multiples of
# ten until one of them fits.

_intervals = [0.10, 0.25, 0.50, 1.00]
_multiple = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000]

import gtk
import drawing

def _calc_interval(max, min, height, minpix, yscale):
    """ Calculate the interval in units of price. Height is the number of
    pixels being used. max is maximum price and min is the minimum price being
    displayed. minpix is the minimum number of pixels between a yscale mark.
    """
    #print "calc interval max ", max, " min ", min, " height ", height, \
    #      " minpix ", minpix, " yscale ", yscale
    found = 0
    for m in _multiple:
        if found == 1:
            break
        for i in _intervals:
            ci = i * m
            if ci * yscale >= minpix:
                found = 1
                break
    #print "ci = ", ci
    return ci

def _cal_ystart(interval, ymin):
    ystart = int(ymin / (interval * 10))
    ystart *= interval
    while ystart < ymin:
        ystart += interval
    return ystart

def draw(ymax, ymin, scale_x1, x1, y1, height, \
         width, yscale, lowest, \
         scale_area, horizontal_grid_lines, minpix=20):
    interval = _calc_interval(ymax, ymin, height, minpix, yscale)
    drawline = drawing.drawline
    drawtext = drawing.drawtext
    drawpoints = drawing.drawpoints
    grey = drawing.colour('grey')
    drawline(grey, scale_x1+3, y1, scale_x1+3, y1 + height)
    ystart = _cal_ystart(interval, ymin)
    font = drawing.font('6x10')
    y = ystart
    gridpoints = []
    while (y < ymax):
        yv = y1 + height - ((y - lowest) * yscale)
        drawline(grey, scale_x1, int(yv), scale_x1+3, int(yv))
        drawtext(font, grey, scale_x1+7, int(yv)+5,
                 ("%.2f") % float(str(y)))
        if horizontal_grid_lines:
            for x in range(x1, width+1, 10):
                gridpoints.append((x,yv))
        y += interval
    if horizontal_grid_lines:
        drawpoints(grey, gridpoints)
