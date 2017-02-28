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



# __all__ = [''] -- for later.

import DataSet
import gtk
import drawing
import sys, string, os
import copy
import utils
import XScale
import Date
import TranslateDate
from Scale import *

class ChartStateSaver:
    def __init__(self):
        pass

class ChartStateLoader:
    def __init__(self):
        pass

class Chart:

    def get_file_name(self):
        return self.filename
    def set_file_name(self, fn):
        self.filename= fn

    def get_current_scale(self):
        return self.scale
    def is_same_scale(self, scale):
        if lower(self.get_current_scale) == scale:
            return 1
        else:
            return 0
    def get_daily_dataset(self):
        return self.daily_dataset
    def get_weekly_dataset(self):
        return self.weekly_dataset
    def get_monthly_dataset(self):
        return self.monthly_dataset

    def __init__(self, name, start_bar=-1, numbars=-1, dataset=None,
                 filename=None):
        self.filename = filename
        self.subchart = {} # key is the title of the subchart. Value is the
                           # subchart object.
        self.subchart_order = [] # list of subchart titles in order of display
        self.subchart_coords = [{}] # store y and height values
        self.start_bar = start_bar
        self.numbars = numbars
        self.name = name
        self.drawtrendline = 0
        # assume daily data
        if dataset == None:
            self.daily_dataset = DataSet.DataSet()
        else:
            self.daily_dataset = dataset
        self.weekly_dataset = DataSet.DataSet()
        self.monthly_dataset = DataSet.DataSet()
        
        self.vertical_border = 15   
        self.horizontal_border = 5 
        self.yscale_space = 40 # used in labeling the y axis
        self.xscale_space = 30 # used in labeling the x axis
        self.xscale = -1       # xscale is calculated once at the chart level
        self.prev_values = {}  # used by the draw method to only draw
                               # when needed
        self.prev_values['x'] = -1
        self.prev_values['y'] = -1
        self.prev_values['width'] = -1
        self.prev_values['height'] = -1
        self.prev_values['numbars'] = -1
        self.prev_values['start_bar'] = -1

        self.scale = SCALE_DAILY # default

        self.able_to_draw = 0 # disable drawing.
                              # Used when chart is first created.
        self.x = -1
        self.y = -1
        self.width = -1
        self.height = -1
        self.calc_next_draw = 1
        # ensure that all datasets have a date series.
        TranslateDate.dates_from_daily_to_weekly(self.get_daily_dataset(),
                                                 self.get_weekly_dataset())
        TranslateDate.dates_from_daily_to_monthly(self.get_daily_dataset(),
                                                 self.get_monthly_dataset())
    def daily_to_weekly(self, start_bar):
        return (start_bar - self.get_numbars()) / 5

    def daily_to_monthly(self, start_bar):
        return start_bar / 22 - (self.get_start_bar() - self.get_numbars())
    
    def weekly_to_monthly(self, start_bar):
        return start_bar / 4 - (self.get_start_bar() - self.get_numbars())

    def weekly_to_daily(self, start_bar):
        return start_bar * 5 

    def monthly_to_daily(self, start_bar):
        return start_bar * 22 

    def monthly_to_weekly(self, start_bar):
        return start_bar * 4 

    def set_calc_next_draw(self):
        self.calc_next_draw = 1
    def get_calc_next_draw(self):
        return self.calc_next_draw
    def reset_calc_next_draw(self):
        self.calc_next_draw = 0

    def fit_to_screen(self):
        start = self.get_start_bar()
        num = self.get_numbars()
        length = self.get_total_bars()
        s = length - num 
        if s < 0:
            s = 0
            num = length
        self.set_start_bar(s)
        self.set_numbars(num)

    def translate_start_bar(self, new_scale, old_scale):
        start = 0
        if old_scale == SCALE_DAILY and new_scale == SCALE_WEEKLY:
            start = self.daily_to_weekly(self.start_bar)
        elif old_scale == SCALE_DAILY and new_scale == SCALE_MONTHLY:
            start = self.daily_to_montly(self.start_bar)
        elif old_scale == SCALE_WEEKLY and new_scale == SCALE_MONTHLY:
            start = self.weekly_to_monthly(self.start_bar)
        elif old_scale == SCALE_WEEKLY and new_scale == SCALE_DAILY:
            start = self.weekly_to_daily(self.start_bar)
        elif old_scale == SCALE_MONTHLY and new_scale == SCALE_DAILY:
            start = self.monthly_to_daily(self.start_bar)
        elif old_scale == SCALE_MONTHLY and new_scale == SCALE_WEEKLY:
            start = self.monthly_to_weekly(self.start_bar)
        else:
            print "self.scale has an invalid value", self.scale

    def get_chart_scale(self):
        return self.scale
    
    def set_chart_scale_daily(self):
        # translate_start_bar is called before changing the scale.
        self.translate_start_bar(SCALE_DAILY, self.scale)
        oldscale = self.scale
        newscale = SCALE_DAILY
        old_ds = self.get_current_dataset()
        self.scale = SCALE_DAILY
        ds = self.get_daily_dataset()
        for sc in xrange(0, len(self.subchart_order)):
            scobj = self.subchart[self.subchart_order[sc]]
            scobj.translate(old_ds, ds, oldscale, newscale)
        self.fit_to_screen()
        # the daily dataset should have already been setup so no changes are
        # needed.
        
    def set_chart_scale_weekly(self):
        # translate_start_bar is called before changing the scale.
        self.translate_start_bar(SCALE_WEEKLY, self.scale)
        oldscale = self.scale
        newscale = SCALE_WEEKLY
        old_ds = self.get_current_dataset()
        self.scale = SCALE_WEEKLY
        ds = self.get_weekly_dataset()
        for sc in xrange(0, len(self.subchart_order)):
            scobj = self.subchart[self.subchart_order[sc]]
            scobj.translate(old_ds, ds, oldscale, newscale)
        self.set_calc_next_draw()
        self.fit_to_screen()
        
    def set_chart_scale_monthly(self):
        # translate_start_bar is called before changing the scale.
        self.translate_start_bar(SCALE_MONTHLY, self.scale)
        self.scale = SCALE_MONTHLY
        ds = self.get_monthly_dataset()
        if len(ds.get_headers()) == 0:
            ds.register('date', [])
            ds.register('open', [])
            ds.register('high', [])
            ds.register('low', [])
            ds.register('close', [])
            convert_ohlc_daily_to_monthly(ds, self.get_daily_dataset())
        self.set_calc_next_draw()
        self.fit_to_screen()

    def get_current_dataset(self):
        if self.scale == SCALE_DAILY:
            return self.daily_dataset
        elif self.scale == SCALE_WEEKLY:
            return self.weekly_dataset
        elif self.scale == SCALE_MONTHLY:
            return self.monthly_dataset
        else:
            print "current scale not set"
            sys.exit(1)

    # used to make sure that the chart doesn't try and draw itself before the
    # window manager is ready.
    def can_draw(self, state=None):
        if state == None:
            return self.able_to_draw
        else:
            self.able_to_draw = state
       
    def set_vertical_border(self, xb):
        self.vertical_border = xb
    def get_vertical_border(self):
        return self.vertical_border
    def set_horizontal_border(self, yb):
        self.horizontal_border = yb
    def get_horizontal_border(self):
        return self.horizontal_border
        
    def set_start_bar(self, bar):
        self.start_bar = bar
    def get_start_bar(self):
        start_bar = 0
        if self.start_bar < 0:
            start_bar= len(self.get_current_dataset().get('date'))+self.start_bar
            self.set_start_bar(start_bar)
            if start_bar < 0:
                raise "Invalid Start Bar"
        return self.start_bar

    # believe that numbars is the number of bars that the chart is
    # currently displaying.
    def set_numbars(self, n):
        self.numbars = n
    def get_numbars(self):
        return self.numbars

    def get_xscale(self):
        return self.xscale
    def set_xscale(self, xscale):
        self.xscale = xscale

    def get_total_bars(self):
        return len(self.get_current_dataset().get('date'))

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

    # if the values of start_bar, numbars and the window size are
    # the same from the previous
    # call to this method, then we don't have to do anything.
    def draw(self, win, event, set_pixmap, del_pixmap,
             start_bar=None, numbars=None):
        """ chart arg is a hash from the table.py file, specifically the ChartT
        hash. The draw function calls the subchart draw functions.
        """
        # use temps to save on lookups
        if start_bar == None:
            start_bar = self.get_start_bar()
        else:
            self.set_start_bar(start_bar)
        if numbars == None:
            numbars = self.get_numbars()
        else:
            self.set_numbars(numbars)
        (x, y, width, height) = win.get_allocation()
        self.set_x(x)
        self.set_y(y)
        self.set_width(width)
        self.set_height(height)
        pixmap_x = x
        pixmap_y = y
        pixmap_width = width
        pixmap_height = height
        del_pixmap()
        p = gtk.create_pixmap(win, pixmap_width, pixmap_height)
        s = gtk.create_pixmap(win, pixmap_width, pixmap_height)
        drawing.set_primary_pixmap(p)
        drawing.set_secondary_pixmap(s)
        drawing.set_window(win)
        drawing.set_drawline_func(gtk.draw_line)
        drawing.set_drawrectangle_func(gtk.draw_rectangle)
        drawing.set_drawtext_func(gtk.draw_text)
        drawing.set_drawpoints_func(gtk.draw_points)
        self.set_start_bar(start_bar)
        start_bar = self.get_start_bar()
        self.prev_values['x'] = x
        self.prev_values['y'] = y
        self.prev_values['width'] = width
        self.prev_values['height'] = height
        self.prev_values['numbars'] = numbars
        self.prev_values['start_bar'] = start_bar
        self.draw_background(win, p)
        self.draw_background(win, s)
        width = width - (self.get_horizontal_border() * 2) - self.yscale_space
        self.set_xscale(float(width)/float(numbars))
        dataset = self.get_current_dataset()
        nsubchart = len(self.subchart_order)
        vertical_space = height - (self.get_vertical_border() * \
                                   nsubchart) - self.xscale_space
        if nsubchart > 1:
            # ssh is secondary subchart height
            ssh = 0.0
            ssh = (float(nsubchart) * float(10)) / (float(100) * (float(nsubchart) -1))
            secsubheight = vertical_space * ssh
            prisubheight = vertical_space - ((nsubchart -1) * secsubheight)
            y1 = (self.get_vertical_border() * nsubchart) + \
                 prisubheight + ((nsubchart-1) * secsubheight)
        else:
            prisubheight = vertical_space
            y1 = self.get_vertical_border() + prisubheight
            
        x1 = self.get_horizontal_border()
        XScale.draw(self.dsget('date'), x1, y1, width, self.xscale_space,
                    start_bar, numbars, self.get_xscale(),
                    self.get_vertical_border(), self.get_current_scale())
        for sc in xrange(0, len(self.subchart_order)):
            if sc == 0:
                x1 = self.get_horizontal_border()
                y1 = self.get_vertical_border()
                sbheight = prisubheight
            else:
                x1 = self.get_horizontal_border()
                y1 = (self.get_vertical_border() * (sc + 1)) + \
                     prisubheight + (secsubheight * (sc - 1))
                sbheight = secsubheight
            self.subchart_coords[sc]['y'] = y1
            self.subchart_coords[sc]['height'] = sbheight
            self.subchart[self.subchart_order[sc]].draw(start_bar,
                                  numbars, self.get_xscale(), 
                                  self.get_current_dataset(), x1, y1,
                                  sbheight, width,
                                  self.yscale_space, self.get_calc_next_draw(),
                                  self.get_current_scale())
        self.reset_calc_next_draw()
        set_pixmap(p, s)
        win.draw((pixmap_x, pixmap_y, pixmap_width, pixmap_height))
        

    def draw_background(self, win, pixmap):
        """draw the background. win is the window to use for defaults
        and pixmap is the pixmap to draw the back ground on.
        """
        gtk.draw_rectangle(pixmap, win.get_style().black_gc, gtk.TRUE, 0, 0,
                           win.get_window().width, win.get_window().height)
    
    def add_subchart(self, title, subchart):
        dummyhash = {}
        self.subchart_order.append(title)
        self.subchart[title] = subchart
        self.subchart_coords.append(dummyhash)
        return self
    def del_subchart(self, title):
        del self.subchart[title]
        return self
    def list_subcharts(self):
        return self.subchart.keys()
    def num_subcharts(self):
        return len(self.subchart.keys())
    def get_subchart(self, title):
        return self.subchart[title]
    def subchart_exists(self, title):
        if self.subchart.haskey(title):
            return 1
        else:
            return 0

    # provide wrapper interface to the DataSet class. chart class has-a
    # DataSet class.
    def dsregister(self, title, series):
        self.get_current_dataset().register(title, series)
        return self
    def dsget(self, title):
        return self.get_current_dataset().get(title)
    def dsdelete(self, title):
        self.dataset.delete(title)
        return self
    def dsget_headers(self):
        return self.get_current_dataset().get_headers()
    def dsreplace(self, title, array):
        return self.get_current_dataset().replace(title, array)

    # coordinate translation methods
    # get the date cooresponding to the x pixel value.
    # Apply the current scale information and return the date.
    # Obviously rounding is going to be an issue.
    def translate_x_coord(self, x):
        """translate x coordinate into a date
        Return None if x value is out of range.
        """
        # the x pixel value does not start from 0.
        xborder = self.get_horizontal_border()
        x -= xborder
        xscale = self.get_xscale()
        if x < xborder:
            x = xborder
        if x > self.get_width() + xborder:
            x = self.get_width() + xborder 
        bar = float(x) / float(xscale)
        date = self.dsget('date')
        bar = utils.round(bar)
        if self.get_start_bar() + bar >= len(date):
            return date[-1]
        else:
            return date[self.get_start_bar() + bar]
       
    # convert pixel value to price.
    # Determine what subchart this pixel is in.
    # ask that subchart for the price value.
    def translate_y_coord(self, y):
        """translate y coordinate into a price value.
        """
        for s in self.subchart.keys():
            if self.subchart[s].ycoordinates_partof_subchart(y):
                schart = self.subchart[s]
                break
        else:
            return None
        return schart.convert_pixel_to_price(y)
            
    # take x and y pixel value and return the name of the subchart.
    # check the borders etc of the subcharts till the cooresponding subchart is
    # found and return ''it''.
    def translate_x_y_into_subchart(self, x, y):
        """take the given x and y pixel coordinates and find the cooresponding
        subchart. If the coordinates are bad return None, otherwise return 
        name of the subchart
        """
        for s in self.subchart.keys():
            if self.subchart[s].xycoordinates_partof_subchart(x, y):
                return s
        return None

    # take a name from the dataseries along with the x date value
    # and return the value from the dataseries at that x value.
    def translate_name_x_into_value(self, x, name):
        d = self.dsget(name)
        datehash = self.dsget('date-hash')
        i = datehash[str(x)]
        return d[i]
    
    # used to display the values of the subcharts in the spaces left by the
    # veritcal borders.
    def display_all_values(self, win, x, y):
        date = self.translate_x_coord(x)
        for i in xrange(0, len(self.subchart_order)):
            sc = self.subchart[self.subchart_order[i]]
            sc.display_values(win, date, x, y, self.get_current_dataset())

    # horizontal line
    def display_x_values(self, win, x, y):
        yvalue = self.translate_y_coord(y)
        subchart = self.translate_x_y_into_subchart(x, y)
        if subchart != None:
            self.subchart[subchart].display_y_values(win, yvalue)

    # vertical line
    def display_y_values(self, win, x, y):
        xvalue = self.translate_x_coord(x)
        sc = self.subchart[self.subchart_order[0]]
        sc.display_x_values(win, xvalue)

    def save_chart_state(self, filefd):
        stateList= self.get_chart_state()
        if stateList != None:
            for i in xrange(0, len(stateList)):
                filefd.write(stateList[i])
        return 1

    ## would an instance of a chart load up another instance of a chart?
    def load_chart_state(self, filefd):
        pass
    load_chart_state= staticmethod(load_chart_state)

    def get_chart_state(self):
        """ return a list of the drawables are pickle strings """
        drawable_state = []
        for i in self.subchart.keys():
            subchart= self.subchart[i]
            for l in subchart.get_drawables_state():
                drawable_state.append(l)
        return drawable_state

    def set_drawables_recalc(self):
        for s in self.subchart.keys():
            self.subchart[s].recalc()

    # this code is in the chart class because the 
    def extend_date_series(self, nbars):
        """extend the date series by nbars"""

if __name__ == '__main__':
    import unittest
    import drawable
    import Subchart

    def createFakeDataSet():
        set= {}
        set['date']= []
        set['open']= []
        set['high']= []
        set['low']= []
        set['close']= []
        len= 256
        dateValue= 20000001
        priceValue= 2.5
        for i in xrange(0, len):
            set['date'].append(dateValue)
            dateValue += 1
        for i in xrange(0, len):
            set['open'].append(priceValue)
            set['close'].append(priceValue - 0.5)
            set['high'].append(priceValue + 0.5)
            set['low'].append(priceValue - 1.0)
            priceValue += 1.0
        ds = DataSet.DataSet()
        for x in set.keys():
            ds.register(x, set[x])
        return ds
    
    class test(unittest.TestCase):

        def setUpChart(self):
            c= Chart('fred',1, 255, createFakeDataSet())
            trendline= drawable.TrendLine(None, 1, 1, 2, 20)
            subchart= Subchart.Subchart('fred')
            subchart.add_drawable('trendline', trendline)
            c.add_subchart('subchart1', subchart)
            return c

        def testChart(self):
            c= self.setUpChart()
            f= open('/tmp/chartstate','w')
            stateList= c.get_chart_state()
            c.save_chart_state(f)
            #ch= Chart.load_chart_state(f)
            f.close()
            
    unittest.main()
