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



import YScale
import utils
import drawing
import gtk
import drawable
from Scale import *

defaultFont = drawing.font('6x10')

class Subchart:
    def __init__(self, title, container):
        self.drawables = {}
        self.title = title
        # grid lines are off by default
        self.horizontal_grid_lines = 0
        self.vertical_grid_lines = 0

        self.x = -1
        self.y = -1
        self.width  = -1
        self.height = -1

        self.yscale = -1

        self.highest_high = -1
        self.lowest_low = -1
        self.container= container

    def recalc(self):
        for d in self.drawables.keys():
            self.drawables[d].recalc()

    def get_xscale(self):
        return self.container.get_xscale()

    def get_highest_high(self):
        return self.highest_high

    def is_horizontal_grid_lines_on(self):
        return self.horizontal_grid_lines
    def is_vertical_grid_lines_on(self):
        return self.vertical_grid_lines
    def set_horizontal_grid_lines_off(self):
        self.horizontal_grid_lines = 0
    def set_vertical_grid_lines_off(self):
        self.vertical_grid_lines = 0
    def set_horizontal_grid_lines_on(self):
        self.horizontal_grid_lines = 1
    def set_vertical_grid_lines_on(self):
        self.vertical_grid_lines = 1

    def set_x(self, x):
        self.x = x
    def get_x(self):
        return self.x
    
    def set_y(self, y):
        self.y = y
    def get_y(self):
        return self.y

    def set_width(self, width):
        self.width = width
    def get_width(self):
        return self.width

    def set_height(self, height):
        self.height = height
    def get_height(self):
        return self.height

    def draw(self, start_bar, numbars, xscale, dataset, x1, y1,
             height, width, yscale_area, recalc, chart_scale):
        tmp = 0.0
        highest = None
        lowest = None
        self.set_x(x1)
        self.set_y(y1)
        self.set_height(height)
        self.set_width(width)
        # check for deleted drawables.
        for d in self.drawables.keys():
            if self.drawables[d].get_delete_this():
                self.drawables[d].delete()
                del self.drawables[d]
        # have the drawable recalc or just calc for the time
        if recalc:
            for d in self.drawables.keys():
                if self.drawables[d].is_hidden():
                    continue
                self.drawables[d].calc(start_bar, numbars, dataset)
        # prime the highest and lowest values.
        for d in self.drawables.keys():
            if highest != None and lowest != None:
                break
            if self.drawables[d].is_hidden():
                continue
            h = self.drawables[d].highest(dataset, start_bar,
                                         start_bar + numbars)
            if h != None:
                highest = h
                
            l = self.drawables[d].lowest(dataset, start_bar,
                                           start_bar + numbars)
            if l != None:
                lowest = l
        # calculate the highest and lowest values.
        for d in self.drawables.keys():
            if self.drawables[d].is_hidden():
                continue
            tmp = self.drawables[d].highest(dataset, start_bar,
                                            start_bar + numbars)
            if tmp != None:
                if tmp > highest:
                    highest = tmp
            tmp = self.drawables[d].lowest(dataset, start_bar,
                                           start_bar + numbars)
            if tmp != None:
                if tmp < lowest:
                    lowest = tmp
        range= highest - lowest
        if range == 0.0:
            range = 0.10
        yscale = height / range
        self.set_yscale(yscale)
        self.highest_high = highest
        YScale.draw(highest, lowest, x1 + width, x1, y1, height, width,
                    yscale, lowest, yscale_area, 
                    self.horizontal_grid_lines)
        for d in self.drawables.keys():
            if self.drawables[d].is_hidden():
                continue
            self.drawables[d].draw(start_bar, numbars, xscale, \
                                   dataset, yscale, lowest, \
                                   x1, y1, height, width)

    def set_yscale(self, yscale):
        self.yscale = yscale
    def get_yscale(self):
        return self.yscale

    def create_drawable(self, drawable_name, **args):
        title= ''
        complete_name = "drawable.mk" + drawable_name
        args['container']= self
        dr= apply(eval(complete_name), [], args)
        if args.has_key('title'):
            title= args['title']
        else:
            title= dr.get_title()
        self._add_drawable(title, dr)
        return dr
    
    def _add_drawable(self, title, drawable):
        self.drawables[title] = drawable
        return self
            
    def del_drawable(self, title):
        if self.drawables.has_key(title):
            del self.drawables[title]
        return self

    def get_drawable(self, title):
        if self.drawables.has_key(title):
            return self.drawables[title]
        else:
            return None
    
    def list_drawables(self):
        return self.drawables.keys()
    
    def num_drawables(self):
        return len(self.drawables.keys())
                   
    def drawable_exists(self, title):
        if self.drawable_exists.haskey(title):
            return 1
        else:
            return 0

    def xycoordinates_partof_subchart(self, x, y):
        sx = self.get_x()
        sy = self.get_y()
        swidth = self.get_width()
        sheight = self.get_height()

        if x >= sx and x <= sx + swidth and \
           y >= sy and y <= sy + sheight:
            return 1
        else:
            return 0

    def ycoordinates_partof_subchart(self, y):
        sy = self.get_y()
        sheight = self.get_height()

        if y >= sy and y <= sy + sheight:
            return 1
        else:
            return 0
        
    def convert_pixel_to_price(self, p):
        return self.get_highest_high() - \
               ((float(p) - float(self.get_y())) / self.get_yscale())

    # wrt to the yscale (price) convert x number of pixels to x number of
    # dollars and cents.
    def convert_price_to_pixel(self, p):
        pass

    def get_drawable_at_coords(self, index, xdate, yprice, cc):
        yscale = 1 / self.get_yscale() * 10
        for d in self.drawables.keys():
            drawable = self.drawables[d]
            (upper, lower) = drawable.get_value_at_index(index, cc)
            if upper == None: # trendlines can return None
                continue
            if lower == None: # a single value per bar
                if yprice >= upper - yscale and \
                   yprice <= upper + yscale:
                    return drawable
            elif yprice >= lower - yscale and \
                 yprice <= upper + yscale:
                return drawable
        else:
            return None

    def display_values(self, win, date, x, y, dataset):
        displaystring = ("%.0f ") % (date,)
        for d in self.drawables.keys():
            dr = self.drawables[d]
            drvalue = dr.get_value_at_x(x, dataset, date)
            # dataseries can have a null value at a given point
            if drvalue == None:
                continue
            for l in drvalue:
                # 0 is the title, 1 is the value.
                displaystring += ("%s:%.2f ") % (l[0], l[1])
        y = self.get_y() - 5 
        font = drawing.font('6x10')
        green = drawing.colour('green')
        gtk.draw_text(win, font.get_font(), green.get_colour(),
                      0, y, displaystring)
        del displaystring

    def display_y_values(self, win, yvalue):
        displaystring = ("%.2f ") % (yvalue,)
        font = drawing.font('6x10')
        green = drawing.colour('green')
        y = self.get_y() - 5
        gtk.draw_text(win, font.get_font(), green.get_colour(),
                      0, y, displaystring)
        
    def display_x_values(self, win, date):
        displaystring = ("%.0f ") % (date,)
        font = drawing.font('6x10')
        green = drawing.colour('green')
        y = self.get_y() - 5
        gtk.draw_text(win, font.get_font(), green.get_colour(),
                      0, y, displaystring)

    def translate(self, old_ds, new_ds, oldscale, newscale):
        for l in self.drawables.keys():
            d = self.drawables[l]
            d.scale_translate(old_ds, new_ds, oldscale, newscale)
            
    def get_drawables_state(self):
        state= []
        for x in self.drawables.keys():
            obj= self.drawables[x]
            state.append(obj.saveStr())
        return state
