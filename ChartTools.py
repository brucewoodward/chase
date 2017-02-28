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


# Code to handle the user interaction when gather info from the user to
# draw trendlines, horizontal lines, verital lines, Andrew's pitch fork etc.

import drawing
from gtk import *
import drawable
import dialogues
import string

# little utility function used from the button_press method of the BaseUI
# class

def get_drawable_at_coords(x,y,current_chart):
    """return None if there isn't a drawable, otherwise return the drawable
    """
    xdate= current_chart.translate_x_coord(x)
    date_hash= current_chart.dsget('date-hash')
    index= date_hash[str(xdate)]
    yprice= current_chart.translate_y_coord(y)
    subchart_title= current_chart.translate_x_y_into_subchart(x,y)
    if subchart_title != None:
        subchart= current_chart.get_subchart(subchart_title)
        dr= subchart.get_drawable_at_coords(index, xdate, yprice,
                                            current_chart)
        if dr != None:
            return dr
    else:
        return None

#
# Each class needs to implement the following methods:
# motion_notify (window, event)
# button_press (window, event)
# button_release (window, event)

MOTION_NOTIFY= 1
BUTTON_PRESS= 2
BUTTON_RELEASE= 3

# The BaseUI class provide dummy methods and a description of the current
# event that are catored for.

class BaseUI:
    def __init__(self):
        self.width = None
        self.height = None
        
    def motion_notify(self, current_chart, win, event, gtk_values):
        return self
    def button_press(self, current_chart, win, event, gtk_values):
        return self
    def button_release(self, current_chart, win, event, gtk_values):
        return self

class CancelBaseUI(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)

class NullBaseUI(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)

    ## XXX 5-3-2003.
    ## This code handles right clicking on a drawable.
    def button_press(self, current_chart, win, event, gtk_values):
        if event.button == 3: ## right clicking of a drawable
            if current_chart == None:
                return self
            x= event.x
            y= event.y
            xscale= current_chart.get_xscale()
            num_either_side = 0
            if xscale <= 2.0:
                num_either_side = 1
            elif xscale <= 5.0:
                num_either_side = 2
            elif xscale <= 10.0:
                num_either_side = 3
            else:
                num_either_side = 4
            # generate a series of values based on the value num_either_side
            points = []
            if xscale < 1.0:
                ## the xrange thingy rounds down causing problems for
                ## very small values.
                xscale = 1.0
            for i in xrange(x - (num_either_side * xscale),
                            x + (num_either_side * xscale +1), xscale):
                dr= get_drawable_at_coords(i,y,current_chart)
                if dr != None:
                    break
            else:
                return self

            popup= dr.change_properties_popup()
            if popup:
                popup.popup(None, None, None,
                            event.button, event.time)
                mainloop()
                gtk_values['da'].queue_draw()
                schedule_redraw(gtk_values)

                # this hack is to allow for the drawables to change
                # the state of the UI or kick off another ChartTool
                # class. This was implemented to make the user
                # selected parrallel trendline code work.
                # The execute_charttools method of the drawable is
                # expected to return an instance of a class
                # from the ChartTools modules.
                if "execute_charttools" in dir(dr):
                    rt= dr.execute_charttools()
                    return rt
        else:
            return self

class CrossHairs(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)
        
    def motion_notify(self, current_chart, win, event, gtk_values):
        window, red, event  = line_drawing_common(self, current_chart, win,
                                                 event, gtk_values)
        draw_line(window, red.get_colour(), event.x, 0,
                  event.x, self.height)
        draw_line(window, red.get_colour(), 0, event.y, self.width,
                  event.y)
        current_chart.display_all_values(window, event.x, event.y)
        return self

    def button_press(self, current_chart, win, event, gtk_values):
        if event.button == 3:
            if current_chart != None:
                schedule_redraw(gtk_values)
                return NullBaseUI()
        return self
                
class HorizontalLine(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)

    def motion_notify(self, current_chart, win, event, gtk_values):
        window, red, event = line_drawing_common(self, current_chart, win,
                                                 event, gtk_values)
        draw_line(window, red.get_colour(), 0, event.y, self.width, event.y)
        current_chart.display_x_values(window, event.x, event.y)
        return self

    def button_press(self, current_chart, win, event, gtk_values):
        if event.button == 1:
            ypos= current_chart.translate_y_coord(event.y)
            subchart= current_chart.translate_x_y_into_subchart(
                x=event.x, y=event.y)
            if subchart != None:
                sc= current_chart.get_subchart(subchart)
                sc.create_drawable("HorizontalLine",ypos=ypos)
            schedule_redraw(gtk_values)
            return NullBaseUI()
        elif event.button == 3:
            if current_chart != None:
                schedule_redraw(gtk_values)
                return NullBaseUI()
        return self
    
class VerticalLine(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)

    def motion_notify(self, current_chart, win, event, gtk_values):
        window, red, event= line_drawing_common(self, current_chart, win,
                                                event, gtk_values)
        draw_line(window, red.get_colour(), event.x, 0, event.x, self.height)
        current_chart.display_y_values(window, event.x, event.y)
        return self

    def button_press(self, current_chart, win, event, gtk_values):
        if current_chart == None:
            return self
        schedule_redraw(gtk_values)
        return NullBaseUI()
    
class TrendLine(BaseUI):
    def __init__(self):
        BaseUI.__init__(self)
        self.xstart = -1
        self.ystart = -1
        self.xend = -1
        self.yend = -1
        self.tmp_xend = -1
        self.tmp_yend = -1
        self.subchart = None
        self.xold = -1
        self.yold = -1
        self.xpix = -1
        self.ypix = -1
        
    def motion_notify(self, current_chart, win, event, gtk_values):
        if self.xstart != -1 and self.ystart != -1:
            width = 0
            height = 0
            x1 = 0.0
            y1 = 0.0
            if current_chart == None:
                self
            yellow = drawing.colour('yellow')
            x= event.x
            y= event.y
            subchart= current_chart.translate_x_y_into_subchart(x,y)
            if subchart != self.subchart:
                return self
            s = gtk_values['secondary_pixmap']
            xold= self.xold
            yold= self.yold
            if xold == -1:
                xold = x
            if yold == -1:
                yold = y
            ypix= self.ypix
            xpix= self.xpix
            if xold >= xpix and yold >= ypix:
                x1  = xpix
                y1 = ypix
                width = xold - xpix +1
                height = yold - ypix +1
            elif xold > xpix and yold < ypix:
                x1 = xpix
                y1 = yold
                width = xold - xpix +1
                height = ypix - yold +1
            elif xold <= xpix and yold <= ypix:
                x1 = xold
                y1 = yold
                width = xpix - xold +1
                height = ypix - yold +1
            elif xold < xpix and yold > ypix:
                x1 = xold
                y1 = ypix
                width = abs(xpix - xold) +1
                height = abs(ypix - yold) +1
            else:
                print "what the hello"
                return self
            window = win.get_window()
            draw_pixmap(window,
                        win.get_style().fg_gc[STATE_ACTIVE],
                         s, x1, y1, x1, y1, width, height)
            draw_line(window, yellow.get_colour(), xpix, ypix, x, y)
            self.xold = x
            self.yold = y
        return self

    def button_press(self, current_chart, win, event, gtk_values):
        if event.button == 1:
            xstart = current_chart.translate_x_coord(event.x)
            ystart = current_chart.translate_y_coord(event.y)
            subchart = current_chart.translate_x_y_into_subchart(x=event.x,
                                                                 y=event.y)
            if subchart != None:
                if self.xstart == -1 and self.ystart == -1:
                    self.xstart = xstart
                    self.ystart = ystart
                    self.subchart = subchart
                    self.xpix = event.x
                    self.ypix = event.y
        return self

    def button_release(self, current_chart, win, event, gtk_values):
        if event.button == 1:
            xend = current_chart.translate_x_coord(event.x)
            yend = current_chart.translate_y_coord(event.y)
            sb= current_chart.get_subchart(self.subchart)
            dr= sb.create_drawable("TrendLine",
                               fs=current_chart.get_current_scale(),
                               xstart=self.xstart,
                               ystart=self.ystart,
                               xend=xend,
                               yend=yend)
            current_chart.dsregister(dr.get_title(),[])
            schedule_redraw(gtk_values)
            return NullBaseUI()
        return self

class TrendlineGuts:
    def __init__(self):
        pass

    def draw_trendline(self):
        raise "draw_trendline method is supposed to be overriden"

    def motion_notify(self, current_chart, win, event, gtk_values):
        return self.generic_event_handler(MOTION_NOTIFY, current_chart,
                                          win, event, gtk_values)

    def button_press(self, current_chart, win, event, gtk_values):
        return self.generic_event_handler(BUTTON_PRESS, current_chart,
                                          win, event, gtk_values)

    def button_release(self, current_chart, win, event, gtk_values):
        return self.generic_event_handler(BUTTON_RELEASE, current_chart,
                                          win, event,  gtk_values)

    def generic_event_handler(self, event_type, current_chart, win, event,
                              gtk_values):
        if self.current_chart == None:
            self.current_chart = current_chart
        if self.gtk_values == None:
            self.gtk_values = gtk_values
        if event_type == MOTION_NOTIFY:
            self.obj = self.obj.motion_notify(current_chart, win, event,
                                              gtk_values)
        elif event_type == BUTTON_PRESS:
            self.obj = self.obj.button_press(current_chart, win,
                                             event, gtk_values)
        elif event_type == BUTTON_RELEASE:
            self.obj = self.obj.button_release(current_chart, win, event,
                                           gtk_values)
        if isinstance(self.obj, NullBaseUI):
            self.draw_trendline()
            schedule_redraw(self.gtk_values)
            return NullBaseUI()
        elif isinstance(self.obj, CancelBaseUI):
            schedule_redraw(self.gtk_values)
            return NullBaseUI()
        else:
            return self


                                        
# To implement Andrews Pitch Fork
# Get the subchart.
# Get the first point.
# Get the second point.
# Get the third point.
# Calculate the points necessary to draw the three trendlines.
# Draw the trendlines and make sure that they extend to the right.
class AndrewsPitchFork(TrendlineGuts,BaseUI):

    def add_drawables(self, drawables):
        # expect the variable drawables to be a list of drawables from the
        # selected subchart.
        self.drawables = drawables

    def get_drawables(self):
        return self.drawables
    
    class SelectSubchart(BaseUI):
        def __init__(self, parent):
            BaseUI.__init__(self)
            self.parent = parent
            
        def return_next_class(self):
            return AndrewsPitchFork.SelectFirstPoint(self.parent)
        
        def button_press(self, current_chart, win, event, gtk_values):
            if event.button == 1:
                subchart_name = current_chart.translate_x_y_into_subchart(
                    x=event.x, y=event.y)
                if subchart_name != None:
                    self.parent.subchart= subchart_name
                    subchart_obj= current_chart.get_subchart(subchart_name)
                    dr= subchart_obj.list_drawables()
                    dsNames= []
                    for d in dr:
                        ds = subchart_obj.get_drawable(d)
                        for dd in ds.list_dataseries():
                            dsNames.append(d + ':' + dd)
                        self.parent.add_drawables(dsNames)
                    return self.return_next_class()
            return self

    class SelectPointWithDrawable(BaseUI):
        def __init__(self, parent, varname):
            BaseUI.__init__(self)
            self.parent = parent
            self.parent.obj = NullBaseUI()
            self.cancelled = 0
            # rt is a string of the form <drawable>:<dataseries>
            rt = dialogues.chose_point(parent.get_drawables())
            if rt != "cancelled":
                self.parent.convert(varname, string.split(rt, ":")[1])
            else:
                self.cancelled = 1
            return None

    class SelectorVerticalLine(BaseUI):
        def __init__(self, parent, next_class, xvar_name, yvar_name):
            BaseUI.__init__(self)
            self.vertical_line = VerticalLine()
            self.parent = parent
            self.next_class = next_class
            self.xvar_name = xvar_name
            self.yvar_name = yvar_name

        def return_next_class(self):
            return eval(self.next_class)
        
        def motion_notify(self, current_chart, win, event, gtk_values):
            self.vertical_line.motion_notify(current_chart, win, \
                                             event, gtk_values)
            return self
        
        def button_press(self, current_chart, win, event, gtk_values):
            if event.button == 1:
                exec("self.parent.%s = %s" % (self.xvar_name,
                     current_chart.translate_x_coord(event.x)))
                subchart = current_chart.translate_x_y_into_subchart(
                    x=event.x, y=event.y)
                if subchart == self.parent.subchart:
                    p= AndrewsPitchFork.SelectPointWithDrawable(self.parent,
                                                                self.yvar_name)
                    if p.cancelled == 1:
                        return CancelBaseUI()
                    else:
                        return self.return_next_class()
            elif event.button == 2 or event.button == 3:
                return CancelBaseUI()
            else:
                return self

    # these next three classes are drawing vertical lines for us only.
    class SelectFirstPoint(SelectorVerticalLine):
        def __init__(self, parent):
            AndrewsPitchFork.SelectorVerticalLine.__init__(self,
                    parent,
                    "AndrewsPitchFork.SelectSecondPoint(self.parent)",
                    "xfirstpoint", "yfirstpoint")
            self.parent = parent
            
    class SelectSecondPoint(SelectorVerticalLine):
        def __init__(self, parent):
            AndrewsPitchFork.SelectorVerticalLine.__init__(self,
                    parent,
                    "AndrewsPitchFork.SelectThirdPoint(self.parent)",
                    "xsecondpoint", "ysecondpoint")
            self.parent = parent
            
    class SelectThirdPoint(SelectorVerticalLine):
        def __init__(self, parent):
            AndrewsPitchFork.SelectorVerticalLine.__init__(self,
                    parent, "NullBaseUI()",
                    "xthirdpoint", "ythirdpoint")
            self.parent = parent

    def __init__(self):
        BaseUI.__init__(self)
        self.subchart = None
        self.obj = AndrewsPitchFork.SelectSubchart(self)
        self.xfirstpoint = -1
        self.yfirstpoint = -1
        self.xsecondpoint = -1
        self.ysecondpoint = -1
        self.xthirdpoint = -1
        self.ythirdpoint = -1
        self.drawables = []
        self.current_chart = None
        self.gtk_values = None

    def draw_pitchforks(self):
        date_hash= self.current_chart.dsget('date-hash')
        date= self.current_chart.dsget('date')
        ## take the dates and make them into indexes into the dataseries
        yvalues= []
        yvalues.append(self.current_chart.translate_name_x_into_value(
            self.xfirstpoint, self.yfirstpoint))
        yvalues.append(self.current_chart.translate_name_x_into_value(
            self.xsecondpoint, self.ysecondpoint))
        yvalues.append(self.current_chart.translate_name_x_into_value(
            self.xthirdpoint, self.ythirdpoint))
        ## Cal. where the pitchforks will go.
        ymidpoint= abs(yvalues[1]-yvalues[2]) / 2
        xmidpoint= abs(date_hash[str(self.xsecondpoint)]-date_hash[str(self.xthirdpoint)])/2
        ## Adjust the values to start from the relevant selected point.
        if self.xsecondpoint < self.xthirdpoint:
            xmidpoint = date[date_hash[str(self.xsecondpoint)] + xmidpoint]
        elif self.xsecondpoint > self.xthirdpoint:
            xmidpoint = date[date_hash[str(self.xthirdpoint)] + xmidpoint]
        else:
            # display message box saying that the values were illegal and
            # then abort.
            pass
        if yvalues[1] < yvalues[2]:
            ymidpoint += yvalues[1]
        elif yvalues[1] > yvalues[2]:
            ymidpoint += yvalues[2]
        else:
            # display message box saying that the values are illegal and
            # then abort.
            pass
        ## cal. the gradient.
        gradient= (ymidpoint-yvalues[0]) / (date_hash[str(xmidpoint)]-date_hash[str(self.xfirstpoint)])
        lright= abs(gradient - yvalues[1])
        lleft= abs(gradient - yvalues[2])
        xright= date[date_hash[str(self.xsecondpoint)]-1]
        xleft= date[date_hash[str(self.xthirdpoint)]-1]
                     
        ## cal second point for two other trendlines.
        
        ## TrendLine constructor wants.
        ## xstart (date value), ystart, yend, xend (date value)
        # draw the middle line.
        sc= self.current_chart.get_subchart(self.subchart)
        dr= sc.create_drawable("TrendLine",
                           fs=self.current_chart.get_current_scale(),
                           xstart=self.xfirstpoint,
                           ystart= yvalues[0],
                           xend= xmidpoint,
                           yend= ymidpoint)
        self.current_chart.dsregister(dr.get_title(),[])
        dr.set_continue_right(1)
        # left or lower pitch fork.
        dr= sc.create_drawable("TrendLine",
                               fs=self.current_chart.get_current_scale(),
                               xstart= xleft,
                               ystart= lleft,
                               xend= self.xthirdpoint,
                               yend= yvalues[2])
        dr.set_continue_right(1)
        self.current_chart.dsregister(dr.get_title(), [])
        # right or upper pitch fork.
        dr= sc.create_drawable("TrendLine",
                               fs=self.current_chart.get_current_scale(),
                               xstart= xright,
                               ystart= lright,
                               xend= self.xsecondpoint,
                               yend= yvalues[1])
        dr.set_continue_right(1)
        self.current_chart.dsregister(dr.get_title(), [])


    def draw_trendline(self):
        self.draw_pitchforks()
        
    def convert(self, varname, name):
        exec("self.%s = '%s'" % (varname, name))


# AssistedTrendline works by using other internal and external classes to
# the work. This avoids if/then/else chains and internal state variables
# except for the variable that hode the instance of the current class.
#
# An internal class, SelectSubchart, is used initially to have the user
# indicate which subchart the AssistedTrendline is going to be drawn in.
#
# Sequence of events:
# (user selects subchart to draw the trendline in)
# class = SelectSubchart. 
# (user selects day via a vertical bar for the start of the trendline)
# class = VerticalLine.
# (user selects point in the subchart via a dialogue that lists the available
# drawables.)
# class = SelectPointWithDrawables. 
# (user select day via a vertical bar for the end of the trendline)
# class = VerticalLine.
# (user selects point in the subchart via a dialogue that lists the available
# drawables.)
# class = SelectPointWithDrawables. 
# (trendline is created)
# class = Trendline.

class AssistedTrendline(TrendlineGuts,BaseUI):

    def add_drawables(self, drawables):
        # expect the variable drawables to be a list of drawables from the
        # selected subchart.
        self.drawables = drawables

    def get_drawables(self):
        return self.drawables

    class SelectSubchart(BaseUI):
        def __init__(self, parent):
            BaseUI.__init__(self)
            self.parent = parent
            
        def return_next_class(self):
            return AssistedTrendline.VerticalLineStart(self.parent)
        
        def button_press(self, current_chart, win, event, gtk_values):
            if event.button == 1:
                subchart_name = current_chart.translate_x_y_into_subchart(
                    x=event.x, y=event.y)
                if subchart_name != None:
                    self.parent.subchart= subchart_name
                    subchart_obj= current_chart.get_subchart(subchart_name)
                    dr= subchart_obj.list_drawables()
                    dsNames= []
                    for d in dr:
                        ds = subchart_obj.get_drawable(d)
                        for dd in ds.list_dataseries():
                            dsNames.append(d + ':' + dd)
                        self.parent.add_drawables(dsNames)
                    return self.return_next_class()
            elif event.button == 2 or event.button == 3:
                return CancelBaseUI()
            else:
                return self

    class VerticalLineStart(BaseUI):
        def __init__(self,parent):
            BaseUI.__init__(self)
            self.vertical_line = VerticalLine()
            self.parent = parent
            
        def return_next_class(self):
            return AssistedTrendline.VerticalLineEnd(self.parent)
        
        def motion_notify(self, current_chart, win, event, gtk_values):
            self.vertical_line.motion_notify(current_chart, win, \
                                             event, gtk_values)
            return self
        
        def button_press(self, current_chart, win, event, gtk_values):
            if event.button == 1:
                xstart = current_chart.translate_x_coord(event.x)
                ystart = current_chart.translate_y_coord(event.y)
                subchart = current_chart.translate_x_y_into_subchart(x=event.x,
                                                                     y=event.y)
                if subchart == self.parent.subchart:
                    self.parent.xstart = xstart
                    self.parent.obj = NullBaseUI()
                    p= AssistedTrendline.SelectFirstPointWithDrawables(self.parent)
                    if p.cancelled == 1:
                        return CancelBaseUI()
                    else:
                        return self.return_next_class()
            elif event.button == 2 or event.button == 3:
                return CancelBaseUI()
            else:
                return self

    class SelectFirstPointWithDrawables(BaseUI):
        def return_next_class(self):
            return AssistedTrendline.VerticalLineStartEnd(self.parent)

        def __init__(self, parent):
            BaseUI.__init__(self)
            self.parent = parent
            self.cancelled = 0
            # turn of events while we are in the chose_point dialogue.
            self.parent.obj = NullBaseUI()
            # rt is a string of the form <drawable>:<dataseries>
            rt = dialogues.chose_point(parent.get_drawables())
            if rt != "cancelled":
                self.parent.convert_start_name_to_value(rt)
            else:   
                self.cancelled = 1
            return None
        
        def motion_notify(self, current_chart, win, event, gtk_values):
            return self
        def button_press(self, current_chart, win, event, gtk_values):
            return self
        def button_release(self, current_chart, win, event, gtk_values):
            return self

    class VerticalLineEnd(BaseUI):
        def __init__(self,parent):
            BaseUI.__init__(self)
            self.vertical_line = VerticalLine()
            self.parent = parent
            
        def return_next_class(self):
            return NullBaseUI()
        
        def motion_notify(self, current_chart, win, event, gtk_values):
            self.vertical_line.motion_notify(current_chart, win, event,\
                                             gtk_values)
            return self
        
        def button_press(self, current_chart, win, event, gtk_values):
            if event.button == 1:
                xend= current_chart.translate_x_coord(event.x)
                yend = current_chart.translate_y_coord(event.y)
                subchart = current_chart.translate_x_y_into_subchart(x=event.x,
                                                                     y=event.y)
                if subchart == self.parent.subchart:
                    # very naughty, writing to the parent.
                    self.parent.gtk_values = gtk_values
                    self.parent.xend = xend
                    self.parent.obj = NullBaseUI()
                    p= AssistedTrendline.SelectEndPointWithDrawables(self.parent)
                    if p.cancelled == 1:
                        return CancelBaseUI()
                    else:
                        return self.return_next_class()
            elif event.button == 2 or event.button == 3:
                return CancelBaseUI()
            else:
                return self
        
    class SelectEndPointWithDrawables(BaseUI):
        def __init__(self, parent):
            BaseUI.__init__(self)
            self.parent = parent
            self.parent.obj = NullBaseUI()
            self.cancelled = 0
            
            rt = dialogues.chose_point(parent.get_drawables())
            if rt != "cancelled":
                self.parent.convert_end_name_to_vales(rt)
            else:
                self.cancelled = 1
            return None
        
        def return_next_class(self):
            return NullBaseUI()
        
        def motion_notify(self, current_chart, win, event, gtk_values):
            return self
        def button_press(self, current_chart, win, event, gtk_values):
            return self
        def button_release(self, current_chart, win, event, gtk_values):
            return self
        
    def __init__(self):
        BaseUI.__init__(self)
        TrendlineGuts.__init__(self)
        # self.obj is the current obj that is in use to handle input.
        self.obj = AssistedTrendline.SelectSubchart(self)
        self.xstart = -1
        self.ystart = -1
        self.xend = -1
        self.xstart = -1
        self.subchart = None
        self.drawables = []
        self.current_chart = None
        self.gtk_values = None

    # the current_chart value isn't around but the event handlers get it
    # so pinch it when they are called and store it away.
    def convert_start_name_to_value(self, name):
        self.ystart = self.current_chart.translate_name_x_into_value(
            self.xstart, string.split(name,':')[1])
        
    def convert_end_name_to_vales(self, name):
        self.yend = self.current_chart.translate_name_x_into_value(
            self.xend, string.split(name,':')[1])

    def draw_trendline(self):
        sc= self.current_chart.get_subchart(self.subchart)
        tr = sc.create_drawable("TrendLine",
                                fs= self.current_chart.get_current_scale(),
                                xstart= self.xstart,
                                ystart= self.ystart,
                                xend= self.xend,
                                yend= self.yend)
        self.current_chart.dsregister(tr.get_title(), [])

# Parrallel Line notes -
# what is going to happen here?
# steps to be performed.
# 1- find out which trendline to parrallel.
# Have the user click on the trendline. If the user clicks on an invalid
# or wrong part of the screen, put a message complaining and then continue
# right on with the task.
# 2- get the gradient of the trendline.
# Now that the user has clicked on a valid piece of drawable, draw a
# trendline on as much of the screen as possible using the gradient of the
# selected trendline.
# 3- Once the user clicks on the left mouse button have the trendline be
# drawn on the spot. woot!
#
# If the user clicks of the left mouse button, consider this a cancellation
# of the operation and abort.
#
# throughts: believe that this would be stateful. Only really three states.
# 1) Having the user select the trendline and 2) constantly redrawing the line
# while the user decides where the line should go. 3) drawing the trendline
# at the choosen spot.
#
# Mar 18 2003.
# !!! stop everything. This is mute because the user selects the trendline
# from the drawable's popup menu. The issue is to put the CurrentObject (or
# whatever it's called) into a state where this class is it's value, from
# way down in the drawables code.
# Mar 19 2003.
# Need to implement both forms. What the user to be able to select the
# trendline to parrallel and also want the user to be able to right click
# on the trendline and use it for drawing a parrellel line.
#
# Have to add code to chase to be able to cope with this requirement.
# Problem: How will the drawable communicate with the top level chase code
# and leave it a command to execute or change it's state?
# Possible solution: Create an extern package that provides a list of
# commands to send to the chase code. It would be even better if this was
# abstracted even further, so that there was a function that the drawable
# called to have the command setup in the chase code. Where to put the
# this function.
#
class ParrallelTrendline(BaseUI):

    class SelectDrawables(BaseUI):
        def __init__(self, parent):
            self.parent = parent
            BaseUI.__init__(self)

    def __init__(self):
        BaseUI.__init__(self)

# this class is used to draw a trendline from the popup menu of the
# trendline drawable. loopback.py always makes use of this class.
#
# This class isn't going to be able to inherit from TrendlineGuts
# because it is going to need to use it's own motion_notify method. hmmm,
# we'll see.
#
# Already have the trendline drawable that is going to be used as a base.
# 1. Get the gradient from the trendline.
# 2. Draw a line in the correct direction using the gradient to the edge
#    of the screen.
# 3. When the user clicks the left mouse button, create a new trendline
#    drawable by calculating the previous point in on the chart.
# 4. If the user clicks the right mouse button make the parrallel trendline
#    stuff disappear.
class ParrallelTrendlineFromExisting(BaseUI):
    def __init__(self,gradient,yscale,xscale):
        BaseUI.__init__(self)
        # the gradient's unit is price per bar.
        self.gradient = gradient
        self.yscale = yscale
        self.xscale = xscale
        self.m = self.gradient * (self.yscale / self.xscale)  
        self.m = -self.m

    # the trendline will always be drawn from the point to the right
    # either sloping up or down.
    def motion_notify(self, current_chart, win, event, gtk_values):
        # make sure that the line is not on the edge of the screen.
        tmp_width= gtk_values['da'].get_window().width
        tmp_height= gtk_values['da'].get_window().height
        if event.x >= tmp_width or event.y >= tmp_height:
            return self
        
        yellow = drawing.colour('yellow')
        # line_drawing_common will add a height and width variable to the
        # class.
        window, red, event = line_drawing_common(self, current_chart, win,
                                                 event, gtk_values)
        x1= event.x
        y1= event.y
        # y2 = m (x2 - x1) * y1
        y2= self.m * (self.width - x1) + y1
        if y2 > self.height:  # touching the bottom of the chart.
            y2 = self.height
        x2= (y2 - y1) / self.m + x1
        draw_line(window, yellow.get_colour(), x1, y1, x2, y2)
        self.xstart = x1
        self.ystart = y1
        self.xend = x2
        self.yend = y2
        return self
    
    def button_press(self, current_chart, win, event, gtk_values):
        if event.button == 1 and self.xstart != None and self.ystart != None:
            # create new trendline.
            # need to translate the xstart, ystart, yend and xend
            # values from pixels into something meaningful.
            # the subchart name is returned.
            sb= current_chart.translate_x_y_into_subchart(x=self.xstart,
                                                          y=self.ystart)
            if sb != None:
                sb= current_chart.get_subchart(sb)
                # calculating the xend and yend values.
                # already have the xstart and ystart values and the yscale
                # and xscale so add the yscale to the ystart and the
                # xscale to the xstart and translate those values.
                xend= self.xstart + self.xscale
                yend= self.m * (xend - self.xstart) + self.ystart
                xend= (yend - self.ystart) / self.m + self.xstart
                dr= sb.create_drawable("TrendLine",
                        fs=current_chart.get_current_scale(),
                        xstart=current_chart.translate_x_coord(self.xstart),
                        ystart=current_chart.translate_y_coord(self.ystart),
                        xend= current_chart.translate_x_coord(xend), 
                        yend= current_chart.translate_y_coord(yend))
                current_chart.dsregister(dr.get_title(),[])
                dr.set_continue_right(1)
                schedule_redraw(gtk_values)
                return NullBaseUI()
            else:
                return self
        elif event.button == 3:  # cancel
            schedule_redraw(gtk_values)
            return NullBaseUI()
        return self
    
    def button_release(self, current_chart, win, event, gtk_values):
        return self

    


## this is probably very evil.
def schedule_redraw(gtk_values):
    gtk_values['redraw'] = 1
    gtk_values['da'].queue_draw()

# this function is miss named. There isn't any line drawing going no.
# instead it updates the screen before drawing a new line.
def line_drawing_common(obj, current_chart, win, event, gtk_values):
    if current_chart == None:
        return
    red = drawing.colour('red')
    s = gtk_values['secondary_pixmap']
    ## Used more than once, so cache it.
    window = win.get_window()
    window= gtk_values['da'].get_window()
    obj.height= window.height
    obj.width= window.width
    draw_pixmap(window,
                win.get_style().fg_gc[STATE_ACTIVE],
                s, 0, 0, 0, 0, window.width, window.height)
    return window, red, event

if __name__ == '__main__':
    import unittest

    class testAssistedTrendline(unittest.TestCase):

        def testInstaniationClas(self):
            s = AssistedTrendline()
            self.assertEquals(isinstance(s, AssistedTrendline),1)

    unittest.main()
