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

import CommonExceptions
import sys
import gtk
import Date
import drawing
from Scale import *

# Months expects to be reference from 1, not 0.
Months = ['!', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
          'Oct', 'Nov', 'Dec']

def _split_date_string(strdate):
    currentdate = str(strdate)
    year = int(currentdate[:4])
    month = int(currentdate[4:6])
    day = int(currentdate[6:8])
    return year, month, day

# Function-Object. Store state so that there is less to keep track off
# once the class has been instantiated.
class mk_draw_vertical_line:
    def __init__(self, gc, drawpoints, xscale, x1, ytop, y1, start_bar):
        self.gc = gc
        self.drawpoints = drawpoints
        self.xscale = xscale
        self.x1 = x1
        self.ytop = ytop
        self.y1 = y1
        self.start_bar = start_bar
    def draw_vertical_line(self, current_bar):
        grid_points = []
        x = ((current_bar - self.start_bar) * self.xscale) + self.x1
        for y  in range(self.ytop, self.y1, 10):
            grid_points.append((x,y))
            self.drawpoints(self.gc, grid_points)

# Another Function-Object.
class mk_write_first_day:
    def __init__(self, font, gc, drawline, drawtext, xscale, start_bar, x1,y1):
        self.font = font
        self.gc = gc
        self.drawline = drawline
        self.drawtext = drawtext
        self.xscale = xscale
        self.start_bar = start_bar
        self.x1 = x1
        self.y1 = y1
    def write_first_day(self, value, i):
        x = ((i - self.start_bar) * self.xscale) + self.x1
        self.drawline(self.gc, x, self.y1, x, self.y1 +3)
        self.drawtext(self.font, self.gc, x, self.y1+15, value)

# Another Function-Object.
class mk_write_new_month:
    def __init__(self, font, gc, drawline, drawtext, xscale, startbar, x1, y1):
        self.font = font
        self.gc = gc
        self.drawline = drawline
        self.drawtext = drawtext
        self.xscale = xscale
        self.startbar = startbar
        self.x1 = x1
        self.y1 = y1
    def write_new_month(self, value, i):
        x = ((i - self.startbar) * self.xscale) + self.x1
        self.drawline(self.gc, x, self.y1+17, x, self.y1+20)
        self.drawtext(self.font, self.gc, x+2, self.y1+25, value)

# Another Function-Object.
class mk_write_new_year:
    def __init__(self, font, gc, drawline, drawtext, x1, y1, xscale, startbar):
        self.font = font
        self.gc = gc
        self.drawline = drawline
        self.drawtext = drawtext
        self.x1 = x1
        self.y1 = y1
        self.xscale = xscale
        self.startbar = startbar
    def write_new_year(self, value, i):
        x = ((i - self.start_bar) * self.xscale) + self.x1
        self.drawline(self.gc, x, y+17, x, y+20)
        self.drawtext(self.font, self.gc, x+2, y+25, value)
    


# Return a class that will draw the xscale for the appropriate xscale value
# and time frame.
class XScaleDraw:
    def _set_defaults(self):
        self.font = drawing.font('6x10')
        self.grey = drawing.colour('grey')

    def __init__(self, current_scale, xscale, x1, y1, width, height, start_bar,
                 numbars, ytop):
        self.internal = None
        self.font = None
        self.grey = None
        self.xscale = xscale
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.height = height
        self.start_bar = start_bar
        self.numbars = numbars
        self.ytop = ytop
        if current_scale == SCALE_DAILY:
            if xscale <= 3.0:
                self.internal = DailyLongTerm()
            elif xscale > 3.0 and xscale < 7.5:
                self.internal = DailyMediumTerm()
            elif xscale >= 7.5:
                self.internal = DailyShortTerm()
        elif current_scale == SCALE_WEEKLY:
            if xscale <= 3.0:
                self.internal = WeeklyLongTerm()
            elif xscale > 3.0 and xscale < 7.5:
                self.internal = WeeklyMediumTerm()
            elif xscale >= 7.5:
                self.internal = WeeklyShortTerm()
        elif current_scale == SCALE_MONTHLY:
            pass
        else:
            sys.stderr.write("XScaleDrawFactory: __init__: Invalid value " +
                             "for current_scale\n")
            sys.exit(1)
        self._set_defaults()
        return None

    def setup_lambda_funcs(self):
        self.wfd = mk_write_first_day(self.font, self.grey, drawing.drawline,
                                      drawing.drawtext, self.xscale,
                                      self.start_bar, self.x1,
                                      self.y1).write_first_day
        
        self.wnm = mk_write_new_month(self.font, self.grey, drawing.drawline,
                                      drawing.drawtext, self.xscale,
                                      self.start_bar, self.x1,
                                      self.y1).write_new_month
        
        self.wny = mk_write_new_month(self.font, self.grey, drawing.drawline,
                                      drawing.drawtext, self.x1, self.y1,
                                      self.xscale,
                                      self.start_bar).write_new_month
        
        self.dvl = mk_draw_vertical_line(self.grey, drawing.drawpoints,
                                         self.xscale, self.x1, self.ytop,
                                         self.y1,
                                         self.start_bar).draw_vertical_line
        

    def draw(self, dates):
        if self.internal != None:
            self.setup_lambda_funcs()
            drawing.drawline(self.grey, self.x1, self.y1,
                             self.x1 + self.width +3, self.y1)
            self.internal.draw(self.wfd, self.wnm, self.wny, dates,
                               self.start_bar, self.numbars, self.dvl)
            
    def set_font(self, font):
        self.font = font
        self.setup_lambda_funcs()

    def set_colour(self, colour):
        self.colour = colour
        self.setup_lambda_funcs()

class DailyTerm:
    def draw(self):
        raise MissingAbstractMethod, "DailyTerm: draw method called"

class DailyShortTerm(DailyTerm):
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        d = Date.Date()
        oldmonth = 0
        oldyear = 0
        for i in xrange(start_bar, start_bar + numbars):
            year, month, day = _split_date_string(dates[i])
            if oldmonth == 0:
                oldmonth = month
            if oldyear == 0:
                oldyear = year
            d.year, d.month, d.day = year, month, day
            if d.weekday() == 0:
                wfd(str(day), i)
                dvl(i)
            if day == 1 or month > oldmonth or year > oldyear:
                wnm(Months[month]+str(year), i)
            oldmonth = month
            oldyear = year
            
class DailyMediumTerm(DailyTerm):
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        oldmonth = 0
        oldyear = 0
        d = Date.Date()
        for i in xrange(start_bar, start_bar + numbars):
            year, month, day = _split_date_string(dates[i])
            if oldmonth == 0:
                oldmonth = month
            if oldyear == 0:
                oldyear = year
            d.year, d.month, d.day = year, month, day
            if day == 1 or month > oldmonth or year > oldyear:
                wnm(Months[month]+str(year),i)
                dvl(i)
                oldmonth = month
                oldyear = year
                

class DailyLongTerm(DailyTerm):
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        prev_year = -1
        prev_month = -1
        d = Date.Date()
        for i in xrange(start_bar, start_bar + numbars):
            year, month, day = _split_date_string(dates[i])
            if prev_year == -1:
                wny(str(year), i)
                if month == 1 and day < 7:
                    wnm(Months[month]+str(year),i)
                dvl(i)
                prev_year = year
            if prev_year < year and day < 7:
                wny(str(year), i)
                if month == 1:
                    wnm(Months[month]+str(year),i)
                dvl(i)
                prev_year = year
                prev_month = 2
            if month % 3 == 0 and prev_month < month and month != 12 \
                   and day < 7:
                prev_month = month
                wnm(Months[month]+str(year), i)
                dvl(i)

class WeeklyTerm:
    def draw(self):
        raise MissingAbstractMethod, "WeeklyTerm: draw method called"
    def draw_xscale(self, wfd, wnm, wny, dates, start_bar, numbars, dvl,
                    every_month, mkstr):
        d = Date.Date()
        oldmonth = 0
        prev_year = 0
        for i in xrange(start_bar, start_bar + numbars):
            year, month, day  = _split_date_string(dates[i])
            if oldmonth == 0:
                oldmonth = month
            if prev_year == 0:
                prev_year = year
            if month > oldmonth and month % every_month == 0 and month != 12 \
               and day < 8:
                wnm(mkstr(month,year),i)
                dvl(i)
                oldmonth = month
            if prev_year < year:
                wnm(mkstr(month,year),i)
                dvl(i)
                oldmonth = 1
                prev_year = year

class WeeklyShortTerm(WeeklyTerm):
    def makestr(self, month, year):
        return Months[month]+str(year)
    
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        self.draw_xscale(wfd, wnm, wny, dates, start_bar, numbars, dvl, 3,
                         self.makestr)
            
class WeeklyMediumTerm(WeeklyTerm):
    def makestr(self, month, year):
        if month == 8 or month == 1:
            return Months[month]+str(year)
        else:
            return Months[month]
    
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        self.draw_xscale(wfd, wnm, wny, dates, start_bar, numbars, dvl, 4,
                         self.makestr)


class WeeklyLongTerm(WeeklyTerm):
    def makestr(self, month, year):
        if month == 1:
            return Months[month]+str(year)
        else:
            return Months[month]
        
    def draw(self, wfd, wnm, wny, dates, start_bar, numbars, dvl):
        self.draw_xscale(wfd, wnm, wny, dates, start_bar, numbars, dvl, 7,
                         self.makestr)
        

# find dates that are either the first trading day of the week or are the
# the first trading day of the month.
# For the case where it's the first day of the week display the day of the
# month.
# For the case where it's the first day in the month display a single letter
# indicating the month.

# The first trading day of the week doesn't have to be monday. Think of the
# case where monday is a public holiday.

# win - gtk drawing window
# dates is the dates array from the DataSet
# x1
# y1
# width
# height
# start_bar
# numbars
def draw(dates, x1, y1, width, height, start_bar, numbars,
         xscale, ytop, current_scale):
    xscaledraw = XScaleDraw(current_scale, xscale, x1, y1, width, height,
                            start_bar, numbars,  ytop)
    xscaledraw.draw(dates)
