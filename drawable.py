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
import sys
import drawing
import utils
import DataSet
import Date
import TranslateDate
import ObjState
from Scale import *

import CommonExceptions
import GtkUtils
import ChartTools

drawable_name_to_class = {'Bar Chart': 'BarChart',
                          'Candle Stick': 'CandleStick',
                          'Swing Chart': 'SwingChart',
                          'RSI': 'RSI',
                          'SMA': 'SMA',
                          'EMA': 'EMA'}

def list_available_drawables():
    return ['Bar Chart', 'Candle Stick', 'Swing Chart', 'RSI', 'SMA', 'EMA']

def list_available_indicators():
    return ['RSI', 'SMA', 'EMA']

def list_available_chart():
    return ['Bar Chart', 'Candle Stick', 'Swing Chart']

def new_drawable_from_name(name):
    new_class = eval(drawable_name_to_class[name] + '()')
    return new_class

def set_end(dataset, end):
    if end == -1:
        return len(dataset.get('date'))
    else:
        return end
    

trendline_title_suffix = 1

# base_drawable is to be inherited by all drawables.
class base_drawable:

    def __init__(self, fs, container): # fs is first_scale
        self.delete_this = 0
        self.title = ''
        self.calculated = 0 # default non-calculated.
        self.scalable = 1   # default is scaled.
        self.translated = 1 # default is to translate drawables.
        self.hidden = 0     # used to make the trendlines go away
        self.first_scale = fs # scale value first created in.
        self.in_scale = 1    # default everything is scaled.
        self.container = container # subchart that we are being displayed on.

    def recalc(self):
        pass

    def set_container(self, container):
        self.container = container
    def get_container(self):
        return self.container

    def get_xscale(self):
        return self.container.get_xscale()
    
    def get_delete_this(self):
        return self.delete_this
    def set_delete_this(self):
        self.delete_this = 1

    def _set_title(self, title):
        self.title = title
    def _get_title(self):
        return self.title

    def _set_calculated(self):
        self.calculated = 1
    def _set_not_calculated(self):
        self.calculated = 0
    def _get_calculated(self):
        return self.calculated

    def _set_scalable(self):
        self.scalable = 1
    def _set_not_scalable(self):
        self.scalable = 0
    def _get_scalable(self):
        return self.scalable

    def set_hidden(self):
        self.hidden = 1
    def get_hidden(self):
        return self.hidden
    def set_not_hidden(self):
        self.hidden = 0
    def is_hidden(self):
        if self.hidden:
            return 1
        else:
            return 0

    def set_first_scale(self, s):
        self.first_scale = s
    def get_first_scale(self):
        return self.first_scale

    def get_in_scale(self):
        return self.in_scale
    def set_in_scale(self, boolean):
        self.in_scale = boolean
    def set_not_in_scale(self):
        self.in_scale = 0

    def list_dataseries(self):
        return [self._get_title()]

    def get_yscale(self):
        return self.container.get_yscale()

    # it is expected that the inheriting class will over this function if
    # needed. Use for the delete funtion would be to remove any dataseries etc.
    def delete(self):
        pass

    def scale_translate(self, dailyds, new_ds, oldscale, new_scale):
        print """scale_translate method is supposed to be overriden by
        inheriting code. Fix this!
        """

HISTOGRAM = 1
LINE = 2

def mkSingleSeries(**args):
    return SingleSeries(args['title'],args['fs'],args['container'])

# SingleSeries class is intended to display information. If you need to
# calculate information based on the values of datasereries, then inherit
# this class and over ride the calc function.
class SingleSeries(base_drawable):
    def __init__(self, title, fs, container):
        base_drawable.__init__(self, fs, container)
        self._set_title(title)
        self.style = HISTOGRAM
        self.colour = 'yellow' # default colour

    
    def delete(self):
        pass

    # display drawable only.
    def calc(self, start_bar, numbars, dataset):
        pass
    
    def draw(self, start_bar, numbars, xscale, ds, yscale, lowest, x1, y1,
             height, width):
        if self.style == HISTOGRAM:
            self._draw_histogram(start_bar, numbars, xscale, ds, yscale,
                                 lowest, x1, y1, height, width)
        elif self.style == LINE:
            self._draw_line(start_bar, numbars, xscale, ds, yscale, lowest,
                            x1, y1, height, width)
        else:
            print "invalid style of SingleSeries"
            sys.exit(1)
            
    def highest(self, dataset, start=0, end=-1):
        values = dataset.get(self._get_title())
        if end == -1:
            end = len(values)
        return max(values[start:end])

    def lowest(self, dataset, start=0, end=-1):
        values = dataset.get(self._get_title())
        if end == -1:
            end = len(values)
        l = min(values[start:end])
        return l
    
    def change_properties_popup(self):
        pass
    
    def get_value_at_index(self, index, cc):
        values = cc.dsget(self._get_title())
        return (values[index], None)

    def _draw_histogram(self, start_bar, numbars, xscale, ds, yscale, lowest,
                        x1, y1, height, width):
        values = ds.get(self._get_title())
        colour = drawing.colour()
        colour.set_colour(self.colour)
        ybottom = (y1 + height) * yscale
        for i in xrange(start_bar, start_bar + numbars):
            x = ((i - start_bar) * xscale) + x1
            yhigh = y1 + height - ((values[i] - lowest) * yscale)
            drawing.drawline(colour, x, yhigh, x, y1 + height)
                        
    def _draw_line(self):
        pass

    # calculating the value of the highest point on the subchart:
    # value = (yheight + (yscale * low)) / yscale

    def get_value_at_x(self, x, dataset, date):
        date_hash = dataset.get('date-hash')
        i = date_hash[str(date)]
        values = dataset.get(self._get_title())
        if values[i] != None: # maybe this is a good thing ???
            return [(self._get_title(), values[i])]
        else:
            return None

    def scale_translate(self, dailyds, newds, oldscale, newscale):
        headers = newds.get_headers()
        ddate = Date.Date()
        # make the assumption that the title and the dataseries are the same.
        title = self._get_title()
        if not title in headers:
            newds.register(title, [])
        # assume here that the scale will always have valid daily data setup.
        # This means that we can never load weekly or montly data.
        if newscale == SCALE_DAILY:
            for h in dailyds.get_headers():
                if h not in headers:
                    pass
        elif newscale == SCALE_WEEKLY:
            date = dailyds.get('date')
            oldvalues = dailyds.get(title)
            newdates= newds.get('date')
            values = newds.get(title)
            if len(values) != 0:
                return
            # find the data for a week and average it over the week.
            # might not be five if there is public holiday
            numdaysinweek = 1
            averagevalue = oldvalues[0]
            for i in xrange(0, len(date)):
                if not TranslateDate.are_dates_in_same_week(date[i-1],date[i]):
                    # first day of a new week.
                    if averagevalue == 0.0 or numdaysinweek == 0:
                        values.append(0.0)
                    else:
                        values.append(float(averagevalue) /
                                      float(numdaysinweek))
                        averagevalue = 0.0
                        numdaysinweek = 1
                else:
                    averagevalue += oldvalues[i]
                    numdaysinweek += 1
            # this should make a part week bar.
            values.append(averagevalue / numdaysinweek)

def mkBarChart(**args):
    fs= args['fs']
    del args['fs']
    container= args['container']
    del args['container']
    return BarChart(fs, container)


class BarChart(base_drawable):

    ## BarChart style class. These are inner classes simply because these
    ## classes will never be used for anything else and it's kinda tidy.

    ## Just inherit from BarChartStyle class.
    class BarChartStyle:
        def __init__(self):
            pass

    class EquiVolumeChart(BarChartStyle):
        def __init__(self):
            pass
        def draw(self, parent, start_bar, numbars, xscale, ds, yscale, lowest,
                 x1, y1, height, width):
            red= drawing.colour('red')
            blue= drawing.colour('blue')
            volume= ds.get('volume')
            open= ds.get(parent.open)
            high= ds.get(parent.high)
            low= ds.get(parent.low)
            close= ds.get(parent.close)
            maxVolume= max(volume[start_bar:start_bar+numbars])
            minVolume= min(volume[start_bar:start_bar+numbars])
            volumeRange= maxVolume - minVolume
            numPixels= xscale
            colour= None
            for i in xrange(start_bar, start_bar+numbars):
                width= ((volume[i]/maxVolume) * numPixels) * 1.25 +3
                x= ((i - start_bar) * xscale) + x1 - (width / 2)
                yhigh= y1 + height - ((high[i] - lowest) * yscale)
                ylow= y1 + height - ((low[i] - lowest) * yscale)
                yclose= y1 + height - ((close[i] - lowest) * yscale)
                if close[i] > open[i]: ## upday
                    drawing.drawrectangle(blue, x, yclose, width,
                                          abs(yclose-ylow), 1)
                    drawing.drawrectangle(blue, x, yhigh, width-1,
                                          abs(yhigh-yclose)+1, 0)
                else: ## down day
                    drawing.drawrectangle(red, x, yhigh, width,
                                          abs(yhigh-yclose)+1, 1)
                    drawing.drawrectangle(red, x, yclose, width-1,
                                          abs(yclose-ylow), 0)

    class StdBarChart(BarChartStyle):
        def __init__(self):
            pass
        def draw(self, parent, start_bar, numbars, xscale, ds, yscale, lowest,
                 x1, y1, height, width):
            tick_length = 2
            green = drawing.colour('green')
            i = start_bar
            end = start_bar + numbars
            open = ds.get(parent.open)
            high = ds.get(parent.high)
            low = ds.get(parent.low)
            close = ds.get(parent.close)
            if xscale >= 15.0:
                tick_length = 3
            for i in xrange(start_bar, end):
                x = ((i - start_bar) * xscale) + x1
                yhigh = y1 + height - ((high[i] - lowest) * yscale)
                ylow = y1 + height - ((low[i] - lowest) * yscale)
                yclose = y1 + height - ((close[i] - lowest) * yscale)
                yopen = y1 + height - ((open[i] - lowest) * yscale)
                drawing.drawline(green, x, yhigh, x, ylow)
                drawing.drawline(green, x, yclose, x + tick_length, yclose)
                drawing.drawline(green, x, yopen, x - tick_length, yopen)

    class CandleStickChart(BarChartStyle):
        def __init__(self):
            pass
        def draw(self, parent, start_bar, numbars, xscale, ds, yscale, lowest,
                 x1, y1, height, width):
            bar_width = 1 ## the actual bar width is bar_width * 2 + 1
            green = drawing.colour('green')
            i  = start_bar
            end = start_bar + numbars
            open = ds.get(parent.open)
            high = ds.get(parent.high)
            low = ds.get(parent.low)
            close = ds.get(parent.close)
            if xscale >= 15.0:
                bar_width = 2
            body_height = 0
            body_width = bar_width * 2 + 1
            fill = 0
            for i in xrange(start_bar, end):
                x = ((i - start_bar) * xscale) + x1
                yhigh = y1 + height - ((high[i] - lowest) * yscale)
                ylow = y1 + height - ((low[i] - lowest) * yscale)
                yclose = y1 + height - ((close[i] - lowest) * yscale)
                yopen = y1 + height - ((open[i] - lowest) * yscale)
                if open[i] > close[i]:  ## down day
                    fill = gtk.TRUE
                    drawing.drawline(green, x, yhigh, x, yopen)
                    drawing.drawline(green, x, yclose, x, ylow)
                    drawing.drawrectangle(green, x - bar_width, yopen,
                                          body_width, abs(yopen - yclose)+1,
                                          fill)
                else:
                    fill = gtk.FALSE
                    drawing.drawline(green, x, yhigh, x, yclose)
                    drawing.drawline(green, x, yopen, x, ylow)
                    drawing.drawrectangle(green, x - bar_width, yclose,
                                          body_width, abs(yopen - yclose)+1,
                                          fill)

                
    class TrueRangeChart(BarChartStyle):
        def __init__(self):
            pass
        def draw(self, parent, start_bar, numbars, xscale, ds, yscale, lowest,
                 x1, y1, height, width):
            pass

        
    def __init__(self, fs, container, **headers):
        base_drawable.__init__(self, fs, container) # fs is first_scale.
                                         # Used by base_drawable
        if not headers:
            self.open = 'open'
            self.close = 'close'
            self.high = 'high'
            self.low = 'low'
        else:
            self.open = headers['open']
            self.high = headers['high']
            self.low = headers['low']
            self.close = headers['close']
        self.style_obj = BarChart.StdBarChart()

    def list_dataseries(self):
        return ['open','high','low','close']

    # we are display only, so there is no calc.
    def calc(self, start_bar, numbars, dataset):
        pass

    def change_style_to(self, style):
        self.style_obj= style
        
    def draw(self, start_bar, numbars, xscale, ds, yscale, \
             lowest, x1, y1, height, width):
        self.style_obj.draw(self, start_bar, numbars, xscale,
                            ds, yscale, lowest, x1, y1, height, width)

    def highest(self, dataset, start=0, end=-1):
        high = dataset.get(self.high)
        if end == -1:
            end = len(high)
        return max(high[start:end])

    def lowest(self, dataset, start=0, end=-1):
        low = dataset.get(self.low)
        if end == -1:
            end = len(low)
        return min(low[start:end])

    def change_properties(self):
        pass

    def get_value_at_index(self, index, cc):
        """Return a tupil represent the upper and lower values of the price
        range at the given index. If there is one dataseries then return
        the tupil (value, None)
        """
        high = cc.dsget('high')
        low = cc.dsget('low')
        return (high[index], low[index])

    def get_value_at_x(self, x, dataset, date):
        date_hash = dataset.get('date-hash')
        i = date_hash[str(date)]
        open = dataset.get(self.open)
        high = dataset.get(self.high)
        low = dataset.get(self.low)
        close = dataset.get(self.close)
        return [('open', open[i]), ('high', high[i]), ('low', low[i]),
                ('close', close[i])]

    def scale_translate(self, dailyds, newds, oldscale, newscale):
        # check for dataseries in the new dataset.
        headers = newds.get_headers()
        if not 'open' in headers:
            newds.register('open', [])
        if not 'high' in headers:
            newds.register('high', [])
        if not 'low' in headers:
            newds.register('low', [])
        if not 'close' in headers:
            newds.register('close', [])
        if len(newds.get('open')) != 0:
            return
        # at this point we can assume that we have necessary headers setup.
        if newscale == SCALE_WEEKLY:
            date = dailyds.get('date') # dailyds is the daily dataset.
            open = dailyds.get('open')
            high = dailyds.get('high')
            low = dailyds.get('low')
            close = dailyds.get('close')
            wdate = newds.get('date')
            wopen = newds.get('open')
            whigh = newds.get('high')
            wlow = newds.get('low')
            wclose = newds.get('close')
            highest = high[0]
            lowest = low[0]
            dailyindex = 0
            prevdayofweek = 7
            weeklyopen = open[0]
            weeklyclose = close[0]
            ddate = Date.Date()
            for i in xrange(1, len(date)):
                # not at the end of the week.
                # Check highest high and lowest low values
                if TranslateDate.are_dates_in_same_week(date[i-1],date[i]):
                    if high[i] > highest:
                        highest = high[i]
                    if low[i] < lowest:
                        lowest = low[i]
                else:
                    # record values concluding the week.
                    wopen.append(weeklyopen)
                    wclose.append(close[i-1])
                    whigh.append(highest)
                    wlow.append(lowest)
                    # record value for the start of the week.
                    weeklyopen = open[i]
                    highest = high[i]
                    lowest = low[i]
            # was the last day visited the end of the week?
            # record values concluding the week.
            wopen.append(weeklyopen)
            wclose.append(close[i])
            whigh.append(highest)
            wlow.append(lowest)

    def popup_style_barchart(self, menu):
        self.change_style_to(BarChart.StdBarChart())
        gtk.mainquit()
        
    def popup_style_candlestick(self, menu):
        self.change_style_to(BarChart.CandleStickChart())
        gtk.mainquit()
        
    def popup_style_truerange(self, menu):
        self.change_style_to(BarChart.TrueRangeChart())
        gtk.mainquit()

    def popup_style_equivolume(self, menu):
        self.change_style_to(BarChart.EquiVolumeChart())
        gtk.mainquit()
        
    def popup_assisted_trendline(self, menu):
        pass

    def change_properties_popup(self, menu=None):
        accelerator = gtk.GtkAccelGroup()
        popup = gtk.GtkMenu()
        popup.set_accel_group(accelerator)
        ## style
        style = gtk.GtkMenuItem(label="Style")
        style.show()
        popup.append(style)
        style_menu = gtk.GtkMenu()
        style.set_submenu(style_menu)
        style_menu.show()

        barchart = gtk.GtkMenuItem(label="Bar Chart")
        barchart.show()
        barchart.connect("activate", self.popup_style_barchart)
        style_menu.add(barchart)

        candlestick = gtk.GtkMenuItem(label="Candle Stick")
        candlestick.show()
        candlestick.connect("activate", self.popup_style_candlestick)
        style_menu.add(candlestick)

        truerange = gtk.GtkMenuItem(label="True Range")
        truerange.show()
        truerange.connect("activate", self.popup_style_truerange)
        style_menu.add(truerange)

        equivolume= gtk.GtkMenuItem(label="Equivolume Chart")
        equivolume.show()
        equivolume.connect("activate", self.popup_style_equivolume)
        style_menu.add(equivolume)
        ##

        assistedtrendline = gtk.GtkMenuItem(label="Assisted Trendline")
        assistedtrendline.show()
        assistedtrendline.connect("activate", self.popup_assisted_trendline)
        popup.append(assistedtrendline)

        popup.show()
        return popup

def mkTrendLine(**args):
    return TrendLine(args['fs'],args['container'],args['xstart'],
                     args['ystart'],args['yend'],args['xend'])
    
class TrendLine(base_drawable, ObjState.State):
    def __init__(self, fs, container, xstart, ystart, yend, xend):
        base_drawable.__init__(self, fs, container)
        ObjState.State.__init__(self)
        if xstart == xend:
            raise "xstart and xend the same value"
        # in the case where a trendline is drawn from right to left the
        # start date will be later than the end date. This breaks, so..
        if xend < xstart:
            tmp= xend
            xend= xstart
            xstart= tmp
            tmp= yend
            yend= ystart
            ystart= tmp

        self.xstart= xstart # date value
        self.xend=  xend # date value
        self.ystart= ystart # price value
        self.yend= yend # price value

        self.continue_right= 0
        self.continue_left= 0

        self.gradient= -1.0
        self.values= []

        self.colour= 'yellow' # default colour
        self._set_trendline_title()
        self.need_recalc= -1
        self.set_not_in_scale() # by default we don't scale the trendline.
        # not any more
        #self._set_not_translated() # trendlines are valid for the time frame
        # drawn only.
        self.execute = ''

    def recalc(self):
        self.values = []
        self._flag_need_recalc()
        
    def execute_charttools(self):
        print "in execute_chartools"
        if self.execute == "parrallel":
            print self.container.title
            return ChartTools.ParrallelTrendlineFromExisting(
                self.get_gradient(), self.get_yscale(), self.get_xscale())
        else:
            return ChartTools.NullBaseUI()
    
    def get_gradient(self):
        return self.gradient

    def reload(infile):
        return ObjState.State._load({'gradient':-1.0, 'values':[]}, infile)
    # the endenting is deliberate.
    reload= staticmethod(reload)

    def _flag_need_recalc(self):
        self.need_recalc= 1

    def get_delete_this(self):
        return self.delete_this

    def _set_gradient(self, m):
        self.gradient = m
        
    def _calc_gradient(self, x1, y1, x2, y2, dataset):
        m = 0.0
        date_hash = dataset.get('date-hash')
        x1_index = date_hash[str(x1)]
        x2_index = date_hash[str(x2)]
        m = (y2 - y1) / (x2_index - x1_index)
        self._set_gradient(m)

    def _recalc_ifneeded(self, start_bar, numbars, dataset):
        if len(self.values) == 0 or self.need_recalc == 1:
            self.calc(start_bar, numbars, dataset)

    def calc(self, start_bar, numbars, dataset):
        self._calc_values(dataset, start_bar, numbars)

    def _fill_in_values(self, date_hash, xstart, ystart, xend,
                        trendline_values):
        m = self.gradient
        xbar = date_hash[str(xstart)]
        for i in xrange(xbar, date_hash[str(xend)]+1):
            if i == None:
                break
            trendline_values[i] = ((i - xbar) * m) + ystart
        self.need_recalc = 0

    def _calc_values(self, dataset, start, end=-1):
        m = 0.0
        self.values = dataset.get(self.get_title())
        dates = dataset.get('date')
        date_hash = dataset.get('date-hash')
        trendline = self.values
        # calculating value for the trendline from the first time only.
        if self.need_recalc == -1: 
            xstart = self.xstart
            xend = self.xend
            ystart = self.ystart
            if end == -1:
                len(dates)
            self._calc_gradient(self.xstart, self.ystart, self.xend,
                                self.yend, dataset)
            # prime the values array
            for i in xrange(0, len(dates)):
                trendline.append(None) # none means 'no value'
            self._fill_in_values(date_hash, xstart, ystart, xend, trendline)
        if self.need_recalc == 1:
            if not date_hash.has_key(str(self.xstart)): # none ourself away
                for i in xrange(0, len(dates)):
                    # this is kinda nasty. Shouldn't happen too oftern but.
                    try:
                        trendline[i] = None
                    except:
                        trendline.append(None)
            else:
                # move xend left if needed.
                if not date_hash.has_key(str(self.xend)):
                    self.xend = dates[-1]
                # grow the array out
                for i in xrange(0, len(dates)):
                    try:
                        trendline[i] = None
                    except:
                        trendline.append(None)
                self._fill_in_values(date_hash, self.xstart, self.ystart,
                                     self.xend, trendline)
        if self.get_continue_right():
            m = self.gradient
            xend = self.xend
            xbar = date_hash[str(xend)]
            yend = self.yend
            for i in xrange(xbar, len(dates)):
                v = ((i - xbar) * m) + yend
                if v < 0:
                    break
                trendline[i] = v
            self.xend = dates[-1]
            self.set_continue_right(0)
        if self.get_continue_left():
            m = self.gradient
            xstart = self.xstart
            ystart = self.ystart
            xbar = date_hash[str(xstart)]
            for i in xrange(0, xbar):
                v = ((i - xbar) * m) + ystart
                if v > 0:
                    trendline[i] = v
            self.xstart = dates[0]
            self.set_continue_left(0)

        self.need_recalc = 0

    def get_title(self):
        return self.title

    def set_colour(self, colour):
        self.colour = colour
    def get_colour(self):
        return self.colour
        
    def change_properites(self):
        pass
    
    def highest(self, dataset, start=0, end=-1):
        end = set_end(dataset, end)
        self._recalc_ifneeded(start, start + end, dataset)
        if not self.get_in_scale():
            return None
        date_hash = dataset.get('date-hash')
        # translate from dates to indices
        xstart = date_hash[str(self.xstart)]
        xend = date_hash[str(self.xend)]
        # not on the current display at all.
        if start < xstart and end < xstart:
            return None
        # not on the current diplay at all before from the end.
        if start > xend:
            return None
        if self.gradient > 0: # sloping up from left to right.
            if end < xstart: # assume that start <= end.
                return None
            else:
                return self.values[end-1]
        else: # sloping down from right to left.
            if end < xstart:
                return None
            elif start < xstart:
                return self.values[start]
            else:
                return self.values[xstart]
            
    def lowest(self, dataset, start=0, end=-1):
        end = set_end(dataset, end)
        self._recalc_ifneeded(start, start + end, dataset)
        if not self.get_in_scale():
            return None
        date_hash = dataset.get('date-hash')
        xstart = date_hash[str(self.xstart)]
        xend = date_hash[str(self.xend)]
        if self.gradient > 0:
            if end < xstart:
                return None
            elif end <= xend:
                return self.values[end]
            elif start >= xstart and end <= xend:
                return self.values[end]
            elif start >= xstart and end > xend:
                return xend
            else:
                return None
        else:
            if end < xstart:
                return None
            elif start < xstart and end <= xend:
                return ystart
            elif start >= xstart:
                return self.values[start]
            else:
                return None
        
    
    def draw(self, start_bar, numbars, xscale, ds, yscale, \
             lowest, x1, y1, height, width):
        self._recalc_ifneeded(start_bar, numbars, ds)
        values = ds.get(self.get_title())
        linecolour = drawing.colour(self.get_colour())
        date_hash = ds.get('date-hash')
        highest = (height + (yscale * lowest)) / yscale
        
        # for the interval that is to be drawn, are there any data points
        # of the trendline to be displayed? If not, then return.
        # Else find the find first point to be drawn and stop at that point.
        ## Find the start of the of the trendline data.
        for i in xrange(start_bar, start_bar + numbars):
            if values[i] != None:
                break
        else:
            return # nothing to draw
        first_bar = i # i is now the first bar to draw

        # Move through the trendline datapoints and stop when the trendline
        # is outside of the current window, or above the highest value
        # or below the lowest value.
        ## Find the start of the of the trendline data on this window.
        for i in xrange(first_bar, start_bar + numbars):
            if values[i] == None: # incase we get to the end of the trendline
                break
            if values[i] < lowest or values[i] > highest:
                continue
            else:
                break

        # Move the through the trendline datapoints and stop when the trendline
        # ends or is outside of the current window.
        ## Find the end of the trendline in this window.
        first_bar = i
        for i in xrange(first_bar, start_bar + numbars):
            if values[i] == None:
                break
            if values[i] > highest or values[i] < lowest:
                break
        if values[i] == None:
            last_bar = i - 1
        else:
            last_bar = i
        if first_bar >= last_bar:
            return
        xlinestart = ((first_bar - start_bar) * xscale) + x1
        ylinestart = y1 + height - \
                     ((values[first_bar] - lowest) * yscale)
        xlineend = ((last_bar - start_bar) * xscale) + x1
        ylineend = y1 + height - \
                   ((values[last_bar] - lowest) * yscale)
        drawing.drawline(linecolour, xlinestart,
                         ylinestart, xlineend, ylineend)


    def _set_trendline_title(self):
        global trendline_title_suffix
        title = 'tl' + str(trendline_title_suffix)
        trendline_title_suffix += 1
        self._set_title(title)
        return title

    def set_continue_right(self):
        self.set_continue_right = 1

    def get_continue_left(self):
        return self.continue_left

    def set_continue_left(self, v):
        self.need_recalc = 1
        self.set_continue_left = 1
        
    def get_continue_right(self):
        return self.continue_right

    def set_continue_right(self, v):
        self.continue_right = v
    def get_continue_right(self):
        return self.continue_right

    def popup_delete(self, menu):
        self.set_delete_this()
        gtk.mainquit()

    def popup_colour_red(self, menu):
        self.set_colour('red')
        gtk.mainquit()
        
    def popup_colour_blue(self, menu):
        self.set_colour('blue')
        gtk.mainquit()

    def popup_colour_green(self, menu):
        self.set_colour('green')
        gtk.mainquit()
        
    def popup_colour_yellow(self, menu):
        self.set_colour('yellow')
        gtk.mainquit()
        
    def popup_colour_white(self, menu):
        self.set_colour('white')
        gtk.mainquit()
        
    def popup_left(self, menu):
        self.set_continue_left(1)
        gtk.mainquit()
        
    def popup_right(self, menu):
        self.set_continue_right(1)
        self.need_recalc = 1
        gtk.mainquit()
        
    def popup_both(self, menu):
        self.set_continue_left(1)
        self.set_continue_right(1)
        gtk.mainquit()
        
    def popup_parrallel_line(self, menu):
        self.execute = "parrallel"
        gtk.mainquit()

    def popup_scale(self, menu):
        # toggle the scaling of the trendline.
        if self.get_in_scale():
            self.set_in_scale(0)
        else:
            self.set_in_scale(1)
        gtk.mainquit()
    
    def change_properties_popup(self):
        accelerator = gtk.GtkAccelGroup()
        popup = gtk.GtkMenu()
        popup.set_accel_group(accelerator)
        delete = gtk.GtkMenuItem(label="Delete")
        delete.connect("activate", self.popup_delete)
        delete.show()
        popup.add(delete)

        scale = gtk.GtkMenuItem(label="Scale")
        scale.connect("activate", self.popup_scale)
        scale.show()
        popup.add(scale)
        
        colours = gtk.GtkMenuItem(label="Colours")
        colours.show()
        popup.append(colours)
        colours_menu = gtk.GtkMenu()
        colours.set_submenu(colours_menu)
        colours_menu.show()

        red = gtk.GtkMenuItem(label="red")
        red.show()
        red.connect("activate", self.popup_colour_red)
        colours_menu.add(red)

        blue = gtk.GtkMenuItem(label="blue")
        blue.show()
        blue.connect("activate", self.popup_colour_blue)
        colours_menu.append(blue)

        green = gtk.GtkMenuItem(label="green")
        green.show()
        green.connect("activate", self.popup_colour_green)
        colours_menu.append(green)

        yellow = gtk.GtkMenuItem(label="yellow")
        yellow.show()
        yellow.connect("activate", self.popup_colour_yellow)
        colours_menu.append(yellow)

        white = gtk.GtkMenuItem(label="white")
        white.show()
        white.connect("activate", self.popup_colour_white)
        colours_menu.append(white)

        extend = gtk.GtkMenuItem(label="Extend")
        extend.show()
        popup.append(extend)
        extend_menu = gtk.GtkMenu()
        extend.set_submenu(extend_menu)
        extend_menu.show()

        left = gtk.GtkMenuItem(label="left")
        left.show()
        left.connect("activate", self.popup_left)
        extend_menu.add(left)

        right = gtk.GtkMenuItem(label="right")
        right.show()
        right.connect("activate", self.popup_right)
        extend_menu.append(right)

        both = gtk.GtkMenuItem(label="both")
        both.show()
        both.connect("activate", self.popup_both)
        extend_menu.append(both)

        parrallel = gtk.GtkMenuItem(label="Parrallel Line")
        parrallel.show()
        parrallel.connect("activate", self.popup_parrallel_line)
        popup.append(parrallel)
        
        popup.show()
        return popup
    
    def get_value_at_index(self, index, cc):
        """Return a tupil represent the upper and lower values of the price
        range at the given index. If there is one dataseries then return
        the tupil (value, None)
        """
        tl = cc.dsget(self.title)
        return (tl[index], None)
        
    def get_value_at_x(self, x, dataset, date):
        i = int(x)
        date_hash = dataset.get('date-hash')
        i = date_hash[str(date)]
        if self.values[i] == None:
            return None
        else:
            return [(self._get_title(), self.values[i])]

    def scale_translate(self, dailyds, newds, oldscale, newscale):
        # trendlines are to be hidden unless the newsclass is scale they were
        # first drawn in.
        if newscale == self.get_first_scale():
            self.set_not_hidden()
        else:
            self.set_hidden()

class FixedLines(base_drawable):
    def __init__(self, container):
        self.colour = 'blue' # default colour
        self.need_recalc = 0
        self.set_not_in_scale() # by default we don't scale these lines
        base_drawable.__init__(self, 0.0, container)

    # the calc function doesn't make sense for this type of drawable.
    def calc(self, start_bar, numbars, dataset):
        pass

    def set_colour(self, colour):
        self.colour = colour
    def get_colour(self):
        return self.colour

class VerticalLine(FixedLines):
    def __init__(self, xpos):
        self.xpos = xpos
        FixedLines.__init__(self)

    # the concept of highest and lowest values for a vertical line don't
    # make much sense for us. Also we don't ever want to be able to scale
    # a vertical line.
    def highest(self, dataset, start=0, end=-1):
        return None

    def lowest(self, dataset, start=0, end=-1):
        return None

    def draw(self, start_bar, numbars, xscale, ds, yscale, lowest, x1, y1,
             height, width):
        pass

    def change_properties_popup(self):
        pass

    def get_value_at_index(self, index, cc):
        pass

    def get_value_at_x(self, x, dataset, date):
        pass

    def scale_translate(self, dailyds, newds, oldscale, newscale):
        pass

def mkHorizontalLine(**args):
    return HorizontalLine(args['ypos'],args['container'])

class HorizontalLine(FixedLines):
    def __init__(self, ypos, container):
        self.ypos = ypos
        FixedLines.__init__(self, container)
        self.colour= 'red'
        

    def highest(self, dataset, start=0, end=-1):
        end = set_end(dataset, end)
        if not self.get_in_scale():
            return None
        else:
            return self.ypos

    def lowest(self, dataset, start=0, end=-1):
        return self.highest(dataset, start, end)

    def draw(self, start_bar, numbars, xscale, ds, yscale, lowest, x1, y1,
             height, width):
        colour= drawing.colour(self.colour)
        x2= (numbars * xscale) 
        y= y1 + height - ((self.ypos - lowest) * yscale)
        drawing.drawline(colour, x1, y, x2, y)

    def popup_colour_red(self, _menu):
        self.colour= 'red'
        gtk.mainquit()

    def popup_colour_blue(self, _menu):
        self.colour= 'blue'
        gtk.mainquit()
        
    def popup_colour_green(self, _menu):
        self.colour= 'green'
        gtk.mainquit()
        
    def popup_colour_yellow(self, _menu):
        self.colour= 'yellow'
        gtk.mainquit()
        
    def popup_colour_white(self, _menu):
        self.colour= 'white'
        gtk.mainquit()

    def popup_delete(self, _menu):
        self.set_delete_this()
        gtk.mainquit()
        
    def change_properties_popup(self):
        accelerator= gtk.GtkAccelGroup()
        popup= gtk.GtkMenu()
        popup.set_accel_group(accelerator)

        ## delete
        delete= gtk.GtkMenuItem(label="Delete")
        delete.show()
        popup.append(delete)
        delete.connect("activate", self.popup_delete)
        
        ## colours
        colours= gtk.GtkMenuItem(label="Colours")
        colours.show()
        popup.append(colours)
        colours_menu= gtk.GtkMenu()
        colours.set_submenu(colours_menu)
        colours_menu.show()

        GtkUtils.build_popup_menu(self, "popup_colour", \
                                  GtkUtils.build_sub_popup_menu, \
                                  colours_menu, \
                                  ['red', 'blue', 'green', 'yellow', 'white'])

        return popup
          

    def get_value_at_index(self, index, cc):
        return (self.ypos, self.ypos)

    def get_value_at_x(self, x, dataset, date):
        return [(self.title, self.ypos)]

    def scale_translate(self, dailyds, newds, oldscale, newscale):
        pass

    def get_title(self):
        return str(self.ypos)

    
if __name__ == '__main__':
    import unittest
    import ObjState
    import TranslateDate
    
    ## adding test first code into the drawable code. Want to do test first for
    ## the automatic saving of drawable state.
    ##

    class tests(unittest.TestCase):
        fileName= '/tmp/trendline'
        def testSaveState(self):
            GRADIENT = 1.456
            VALUES = [1.1]
            dr = TrendLine(0, 1, 1, 2, 20)
            xstart= dr.xstart
            ystart= dr.ystart
            xend= dr.xend
            yend= dr.yend
            dr.gradient = GRADIENT
            dr.values = VALUES[:]
            gradient= dr.gradient
            values= dr.values
            file= open(self.fileName, 'w+')
            dr.save(file)
            file.close()

            file= open(self.fileName, 'r+')
            newdr= TrendLine.reload(file)
            self.assertEquals(xstart, newdr.xstart)
            self.assertEquals(ystart, newdr.ystart)
            self.assertEquals(yend, newdr.yend)
            self.assertEquals(xend, newdr.xend)
            self.assertNotEquals(gradient, newdr.gradient)
            self.assertNotEquals(values, newdr.values)
            self.assertEquals(newdr.gradient, -1.0)
            self.assertEquals(newdr.values, [])
            file.close()

        def testLoadState(self):
            self.testSaveState()
            xstart= 1
            ystart= 1
            yend= 2
            xend= 20
            file= open(self.fileName,'r+')
            dr= TrendLine.reload(file)
            self.assertEquals(dr.xstart, xstart)
            self.assertEquals(dr.ystart, ystart)
            self.assertEquals(dr.xend, xend)
            self.assertEquals(dr.yend, yend)
            self.assertEquals(dr.gradient, -1.0)
            self.assertEquals(dr.values, [])

    class testBarChartTranslateFromDailyToWeekly(unittest.TestCase):

        def registerDataSet(self, date, open, high, low, close):
            dailyDataSet= DataSet.DataSet()
            dailyDataSet.register('date', date)
            dailyDataSet.register('open', open)
            dailyDataSet.register('high', high)
            dailyDataSet.register('low', low)
            dailyDataSet.register('close', close)
            newds= DataSet.DataSet()
            return dailyDataSet, newds

        def dummyUpAndRun(self, dailyDataSet, newds):
            oldscale= SCALE_DAILY
            newscale= SCALE_WEEKLY
            TranslateDate.dates_from_daily_to_weekly(dailyDataSet, newds)
            barChart= BarChart(3.0)
            barChart.scale_translate(dailyDataSet, newds, oldscale,
                                     newscale)
            return barChart

        def makeArrays(self):
            date= []
            open= []
            high= []
            low= []
            close= []
            return date, open, high, low, close
            
        def testTranslateFullWeek(self):
            date, open, high, close, low = self.makeArrays()
            # dummy up five days
            initial= 10.0
            expectedOpen= initial
            expectedLow= initial - 1.0
            for x in xrange(20021202, 20021206):
                date.append(x)
                open.append(initial)
                close.append(initial+0.5)
                high.append(initial+1.0)
                low.append(initial-1.0)
                initial += 0.5
            initial -= 0.5
            expectedHigh= initial + 1.0
            expectedClose= initial + 0.5
            dailyDataSet, newds = \
                          self.registerDataSet(date, open, high, low, close)
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(len(newds.get('date')),1)
            self.assertEquals(newds.get('open')[0], expectedOpen)
            self.assertEquals(newds.get('high')[0], expectedHigh)
            self.assertEquals(newds.get('low')[0], expectedLow)
            self.assertEquals(newds.get('close')[0], expectedClose)

        def testTranslateTwoDays(self):
            date, open, high, close, low = self.makeArrays()
            date.append(20021202)
            open.append(10.0)
            close.append(10.5)
            high.append(11.0)
            low.append(9.0)
            date.append(20021203)
            open.append(11.0)
            high.append(12.0)
            low.append(10.5)
            close.append(11.25)
            dailyDataSet, newds= \
                          self.registerDataSet(date, open, high, low, close)
            # should have a weekly chart in the newds DataSet.
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(newds.get('open')[0], 10.0)
            self.assertEquals(newds.get('close')[0], 11.25)
            self.assertEquals(newds.get('high')[0], 12.0)
            self.assertEquals(newds.get('low')[0], 9.0)

        def testTranslateFourDays(self):
            date, open, high, close, low = self.makeArrays()
            initial= 10.0
            expectedOpen= initial
            expectedHigh= initial + 1.0
            for x in xrange(20021202, 20021205):
                date.append(x)
                open.append(initial)
                close.append(initial+0.5)
                high.append(initial+1.0)
                low.append(initial-1.0)
                initial -= 0.5
            initial += 0.5
            expectedLow= initial - 1.0
            expectedClose= initial + 0.5
            dailyDataSet, newds = \
                          self.registerDataSet(date, open, high, low, close)
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(len(newds.get('date')),1)
            self.assertEquals(newds.get('open')[0], expectedOpen)
            self.assertEquals(newds.get('high')[0], expectedHigh)
            self.assertEquals(newds.get('low')[0], expectedLow)
            self.assertEquals(newds.get('close')[0], expectedClose)

        def testTranslateTwoDaysNotStartingMonday(self):
            date, open, high, close, low = self.makeArrays()
            date.append(20021203)
            open.append(10.0)
            close.append(10.5)
            high.append(11.0)
            low.append(9.0)
            date.append(20021204)
            open.append(11.0)
            high.append(12.0)
            low.append(10.5)
            close.append(11.25)
            dailyDataSet, newds= \
                          self.registerDataSet(date, open, high, low, close)
            # should have a weekly chart in the newds DataSet.
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(newds.get('open')[0], 10.0)
            self.assertEquals(newds.get('close')[0], 11.25)
            self.assertEquals(newds.get('high')[0], 12.0)
            self.assertEquals(newds.get('low')[0], 9.0)

        def testTranslateAWeekAndOneDay(self):
            date, open, high, close, low = self.makeArrays()
            initial= 10.0
            expectedOpen= initial
            expectedLow= initial -1.0
            for x in xrange(20021202, 20021206):
                date.append(x)
                open.append(initial)
                close.append(initial+0.5)
                high.append(initial+1.0)
                low.append(initial-1.0)
                initial += 0.5
            initial -= 0.5
            expectedHigh= initial + 1.0
            expectedClose= initial + 0.5
            date.append(20021209)
            open.append(10.0)
            close.append(10.0+0.5)
            high.append(10.0+1.0)
            low.append(10.0-1.0)
            dailyDataSet, newds= \
                          self.registerDataSet(date, open, high, low, close)
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(2, len(newds.get('open')))
            self.assertEquals(newds.get('open')[0], expectedOpen)
            self.assertEquals(newds.get('high')[0], expectedHigh)
            self.assertEquals(newds.get('low')[0], expectedLow)
            self.assertEquals(newds.get('close')[0], expectedClose)
            self.assertEquals(newds.get('open')[1], 10.0)
            self.assertEquals(newds.get('high')[1], 10.0+1.0)
            self.assertEquals(newds.get('low')[1], 10.0-1.0)
            self.assertEquals(newds.get('close')[1], 10.0+.5)

        ## believe that there is a problem with the logic of the code
        ## in the scenario where the current day is tuesday the 8th
        ## and the next day is is thursday 18th. In the scenario
        ## the code would consider this to be the same week because the
        ## current days of the week is 2 and the next day of the week is
        ## 4. So this would appear as though Wednesday was a holiday, when
        ## a large chunk of dates don't exist but is still considered to be
        ## the current week.
        def testTranslateDayAheadNextWeek(self):
            date, open, high, close, low = self.makeArrays()
            initial= 10.0
            for x in (20030106, 20030107, 20030116, 20030117, \
                      20030120, 20030121, 20030122, 20030123, 20030124,
                      20030128):
                date.append(x)
                open.append(initial)
                close.append(initial+0.5)
                high.append(initial+1.0)
                low.append(initial-1.0)
                initial += 0.5
            initial -= 0.5
            dailyDataSet, newds= \
                          self.registerDataSet(date, open, high, low, close)
            self.dummyUpAndRun(dailyDataSet, newds)
            self.assertEquals(4, len(newds.get('date')))
            self.assertEquals(4, len(newds.get('open')))

        def testSingleSeriesScaleTranslate(self):
            date, series = [], []
            value = 10
            dailyDataSet= DataSet.DataSet()
            for x in (20030123,20030124,20030128):
                date.append(x)
                series.append(value)
                value += 1
            ss = SingleSeries("testing", 1)
            dailyDataSet.register('date',date)
            dailyDataSet.register('testing',series)
            weeklyDataSet= DataSet.DataSet()
            TranslateDate.dates_from_daily_to_weekly(dailyDataSet,
                                                     weeklyDataSet)
            ss.scale_translate(dailyDataSet, weeklyDataSet, SCALE_DAILY,
                               SCALE_WEEKLY)
            self.assertEquals(2, len(weeklyDataSet.get('date')))
            self.assertEquals(2, len(weeklyDataSet.get('testing')))
            

    ## testing trendline scale conversion from a higher scale to a lower
    ## should be performed but it really should be a no brainer. Basically
    ## the trendline is re-calculated in the lower scale if it didn't
    ## already exist.
    class testTrendlineScaleConversionDailyToWeekly(unittest.TestCase):
        pass
    class testTrendlineScaleConversionDailyToMonthly(unittest.TestCase):
        pass
    class testTrendlineScaleConversionWeeklyToDaily(unittest.TestCase):
        pass
    class testTrendlineScaleConversionWeeklyToMonthly(unittest.TestCase):
        pass


    class testVerticalLine(unittest.TestCase):
        pass

    class testHorizontalLine(unittest.TestCase):
        pass

    unittest.main()
