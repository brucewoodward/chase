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

from gtk import *
import GDK
import GtkExtra
from datafuncs import *
#import os, os.path, sys, re, string, xreadlines
import os, os.path, sys, re, string
import Chart, Subchart, drawable, dialogues, drawing
from CurrentChart import *
from types import *
from DataSet import *
import custfuncs

import getopt
#import libglade, ChartTools
import ChartTools

chase_glade_class = '' # set by the load_glade_dialogues function.

Gtk_values = {}

chase_options = {}

current_chart = CurrentChart()

current_user_input = ChartTools.NullBaseUI()

#####
#
# '#defined' ....
RC_FILE_PAT = 'rc_file(\s+)?=(\s+)?(.*)'
BASE_PAT    = 'chase_base(\s+)?=(\s+)?(.*)'
STOCK_DIR_PAT = 'stockdir(\s+)?=(\s+)?(.*)'
AUTOLOAD_PAT = 'autoload(\s+)?=(\s+)?(.*)'
REALTIME_PAT = 'realtime(\s+)?=(\s+)?([^,]+,.*)'
RC_FILE     = 'RC_FILE'
CHASE_BASE  = 'CHASE_BASE'
RC_FILE_NAME = '.chase_rc'
STOCK_DIR   = 'STOCK_DIR'
AUTOLOAD_LIST = 'AUTOLOAD_LIST'
REALTIME = 'REALTIME'

real_time_entries = {}

def set_current_user_input(i):
    global current_user_input
    if i != None:
        current_user_input = i

def destory(w):
    gtk._destroy(w)

# win is a reference to the GtkDrawingArea
def draw_current_chart(win, event, set_pixmap, del_pixmap):
    draw_current_chart.x = win.get_window().width
    draw_current_chart.y = win.get_window().height
    chart = current_chart.get_current()
    if chart:
        chart.draw(win, event, set_pixmap, del_pixmap)
        win.show()

def schedule_redraw():
    Gtk_values['redraw'] = 1
    Gtk_values['da'].queue_draw()

def delete_cb(win, event):
    sys.exit(1)

def configure_cb(win, event):  # Drawing Area callback
    cc = current_chart.get_current()
    if cc != None:
        cc.can_draw(1)
        draw_current_chart(win, event, set_pixmap, del_pixmap)
    
def expose_cb(win, event):     # Drawing Area callback
    print "expose_cb called"
    cc = current_chart.get_current()
    if cc != None:
        if cc.can_draw():
            (x, y, width, height) = event.area
            if Gtk_values['redraw'] == 1:
                Gtk_values['redraw'] = 0
                draw_current_chart(win, event, set_pixmap, del_pixmap)
            pm = Gtk_values['primary_pixmap']
            draw_pixmap(win.get_window(),
                        win.get_style().fg_gc[STATE_ACTIVE],
                        pm, x, y, x, y, width, height)
    else:
        print "ignored"

def motion_notify_cb(win, event):  # Drawing Area callback
    global current_user_input
    set_current_user_input(current_user_input.motion_notify(
        current_chart.get_current(), win, event, Gtk_values))
    
def button_press_cb(win, event):
    global current_user_input
    set_current_user_input(current_user_input.button_press(
        current_chart.get_current(), win, event, Gtk_values))
                            
def button_release_cb(win, event):
    global current_user_input
    set_current_user_input(current_user_input.button_release(
        current_chart.get_current(), win, event, Gtk_values))

def reset_draw_trendline():
    #restore_event_mask_after_trendline_drawing()
    reset_draw_trendline_temps() 

def set_pixmap(p, s):
    Gtk_values['primary_pixmap'] = p
    Gtk_values['secondary_pixmap'] = s

def del_pixmap():
    if Gtk_values.has_key('primary_pixmap'):
        dp = Gtk_values['primary_pixmap']
        del dp
    if Gtk_values.has_key('secondary_pixmap'):
        sp = Gtk_values['secondary_pixmap']
        del sp

def get_secondary_pixmap():
    return Gtk_values['secondary_pixmap']

def draw_blank_screen():
    pass
        
# used by tools_tline function to setup trendline drawing.
def set_event_mask_for_trendline_drawing():
    da = Gtk_values['da']
    da.add_events(GDK.POINTER_MOTION_MASK)
    da.add_events(GDK.KEY_PRESS_MASK)
    da.add_events(GDK.BUTTON_PRESS_MASK)
    da.add_events(GDK.BUTTON_RELEASE_MASK)

# restore event mask to original after trendline drawing is complete.
def restore_event_mask_after_trendline_drawing():
    da = Gtk_values['da']
    # the set_events function causes a Gtk-CRITICAL error.
    # assertion `!GTK_WIDGET_REALIZED(widget) failed.`
    # XXX need to understand why.


def set_scroller_values(len, nbars):
    scroller = Gtk_values['scroller']
    scroller.set_all(len - nbars, 0, len +1, 1, nbars, nbars)
    Gtk_values['hscroll_bar'].show()

def create_standard_chart(name, dataset):
    chart = Chart.Chart(name=name, dataset=dataset)
    chart.set_start_bar(-100) # 100 bars from the end
    chart.set_numbars(100)
    sc = Subchart.Subchart(name, chart)
    sc.set_vertical_grid_lines_on()
    sc.set_horizontal_grid_lines_on()
    barchart= sc.create_drawable("BarChart",title='OHLC',
                                 fs=chart.get_current_scale())
    chart.add_subchart('OHLC', sc)
    # setup the volume subchart
    if 'volume' in dataset.get_headers():
        volume = dataset.get('volume')
        scv = Subchart.Subchart('volume', chart)
        scv.set_vertical_grid_lines_on()
        scv.set_horizontal_grid_lines_on()
        volumehisto = scv.create_drawable("SingleSeries",title='volume',
                                            fs=chart.get_current_scale())
        chart.add_subchart('volume', scv)
    set_scroller_values(chart.get_total_bars(), chart.get_numbars())
    return chart

def create_default_chart(name, dataset):
    """ function to create and populate a chart class with default values.
    """
    # currently the default values are set here, but later there will have to
    # be a default module that reads the values from say a .chase file in the
    # users home directory.
    Gtk_values['win'].set_title(name)
    return create_standard_chart(name, dataset)

def setup_loaded_chart(d, file_name):
    ds = DataSet()
    for x in d.keys():
        ds.register(x, d[x])
    name= os.path.basename(file_name)
    chart = create_default_chart(name, ds)
    chart.set_file_name(file_name)
    current_chart.add(name, chart)
    current_chart.set_current(name)
    chart.can_draw(1)
    schedule_redraw()

def load_file(file_name):
    try:
        d = load_data_file(file_name)
    except Exception, msg:
        mb= GtkExtra.message_box(title="Error Loading File",
                             message="Problems Loading File: " + file_name,
                             buttons=("OK",))
        return None
    return d

def load_chart(file_name):
    d= load_file(file_name)
    if d != None:
        ds = DataSet()
        for x in d.keys():
            ds.register(x, d[x])
        name= os.path.basename(file_name)
        chart= create_standard_chart(name, ds)
        chart.set_file_name(file_name)
        chart.can_draw(1)
        current_chart.add(name, chart)


def file_open_ok_button(button, win):
    file_name = win.get_filename()[:]
    d= load_file(file_name)
    win.destroy()
    if d != None:
        setup_loaded_chart(d, file_name)
    
def file_open_cancel_button(button, win):
    win.destroy()
    
def file_open_delete_event(button, win):
    win.destroy()
    
def file_open(menu):
    """ Use GtkFileSelection to get the name of a data file to open.
    """
    filesel = GtkFileSelection()
    filesel.set_title('Select Data File to Display')
    filesel.connect("delete_event", file_open_delete_event, filesel)
    filesel.ok_button.connect("clicked", file_open_ok_button, filesel)
    filesel.cancel_button.connect("clicked", file_open_cancel_button, filesel)
    try:
        filename = chase_options[STOCK_DIR]
    except:
        filename = None
    if filename != None:
        filesel.set_filename(filename)
    filesel.show()

def file_close(_menu):
    cc = current_chart.get_current()
    if cc != None:
        name= current_chart.delete_current()
        if name != None:
            Gtk_values['win'].set_title(name)
            schedule_redraw()
        else:
            Gtk_values['win'].set_title('Nothing loaded')
            draw_blank_screen()

def file_save():
    pass

def update_data_file(data):
    prefix= ''
    try:
        prefix= chase_options[STOCK_DIR]
    except:
        prefix= '/'
    filename= prefix + '/' + data['stock']
    if os.access(filename, os.R_OK | os.W_OK):
        # make the assumption that the new data is either going to be
        # at the last line or after the last line depending upon the value
        # of the date on the last line.
        inf= open(filename, "r+")
        lines= []
        #for line in xreadlines.xreadlines(inf):
        for line in inf:
            lines.append(line)
        inf.close()
        lastdate= float(string.split(lines[len(lines)-1], ',')[0])
        if lastdate < float(data['date']): # appending a line to the file.
            inf= open(filename, "a+")
            inf.write("%.0f,%.3f,%.3f,%.3f,%.3f,%d\n" %
                     (float(data['date']), float(data['open']),
                      float(data['high']), float(data['low']),
                      float(data['current']), int(data['volume'])))
            inf.close()
        else: # updating last line in the file.
            offset= 0
            # at the end of the loop, offset should be at the beginning of the
            # last line.
            for i in lines[:-1]:
                offset += len(i)
            out= open(filename, "r+")
            out.seek(offset)
            # overwrite the last line.
            out.write("%.0f,%.3f,%.3f,%.3f,%.3f,%d\n" %
                     (float(data['date']), float(data['open']),
                      float(data['high']), float(data['low']),
                      float(data['current']), int(data['volume'])))
            # os.tell(0,1) should be the size of the file at the current pos.
            out.truncate(out.tell()) # truncate the file to the current size
            out.close()
        return 1
    else:
        sys.stderr.write("file doesn't exist: %s" % (filename,))
        return 0

def update_chase_with_realtime_data(name):
    inf= open(name)
    files2reload = []
    data= []
    #for line in xreadlines.xreadlines(inf):
    for line in inf:
        data= string.split(line, ',')
        if len(data) != 7:
            sys.stderr.write("Bad line of data: %s" % (line,))
        else:
            rt= update_data_file({'stock':data[0], 'date':data[1],
                                  'open':data[2], 'high':data[3],
                                  'low':data[4], 'current':data[5],
                                  'volume':data[6]})
            if rt == 1:
                files2reload.append(data[0])
    prefix= ''
    try:
        prefix= chase_options[STOCK_DIR]
    except:
        prefix= '/'
    for s in files2reload:
        if current_chart.get(s) == None:
            load_chart(prefix + '/' + s)
        else:
            file_reload_c(s)
    schedule_redraw()

def file_realtime_update(_menu, entry_name):
    if real_time_entries.has_key(entry_name):
        script= real_time_entries[entry_name]
        if os.access(script, os.R_OK | os.X_OK):
            name= os.tempnam('/tmp/', 'chase')
            f=open(name,'w+')
            f.close()
            rt= os.system(script+" -t "+name)
            if rt != 0:
                mb= GtkExtra.message_box(
                    title="Error loading data from %s" % (entry_name,),
                    message="External source failed",
                    buttons=("OK",))
                return None
            print "system command returned %d" % (rt,)
            update_chase_with_realtime_data(name)
            #os.unlink(name)
        else:
            sys.write.stderr("Can't find the script: %s" % (script,))
    else:
        sys.write.stderr("realtime update called with invalid name: %s" \
                         % (entry_name,))

# function loads a file, expecting that filename is the full path to that
# file.
def auto_file_load(filename):
    if filename != None:
        try:
            d= load_data_file(filename)
        except:
            GtkExtra.message_box(title="Error Loading File",
                                 message="Problems Loading File: " + file_name,
                                 buttons=("OK",))
            return None
        setup_loaded_chart(d, filename)

# file_reload_c is a control. No gui attachement.
def file_reload_c(stock):
    cc= current_chart.get(stock)
    if cc != None:
        d= load_file(cc.get_file_name())
        if d == None:
            return None
        else:
            headers= cc.dsget_headers()
            for x in d.keys():
                if x in headers:
                    cc.dsreplace(x, d[x])
                else:
                    cc.dsregister(x, d[x])
            cc.set_drawables_recalc()

# file reload is a view because its arg is a gui.
def file_reload(_menu, stock=None):
    if stock == None:
        stock = current_chart.get_current_name()
    if stock != None:
        file_reload_c(stock)
        schedule_redraw()
        
def file_exit(arg):
    import sys
    sys.exit(0)

def tools_cross_hairs(menu):
    # the work for this code will have to take place in the mouse motion
    # callback.
    # need some way of turning off the cross hairs. Pushing the escape or any
    # of the mouse buttons would be ok.
    set_current_user_input(ChartTools.CrossHairs())

def tools_hline(menu):
    set_current_user_input(ChartTools.HorizontalLine())
    
def tools_vline(menu):
    set_current_user_input(ChartTools.VerticalLine())
    
# trendline call back
def tools_tline(win):
    # set gdk event mask for mouse motion, button press and release and
    # keyboard events. (should write a seperate function to do this).
    # set the chart_state['do_trendline'] to true. Some day it would be nice
    # to be able to change the shape of the mouse pointer so that it's easy
    # to see that we are drawing a trendline. Also add func. to allow for
    # selecting a trendline by date and value of the bar (OHLC).
    set_event_mask_for_trendline_drawing()
    set_current_user_input(ChartTools.TrendLine())
    
def tools_custfuncs(menu):
    custfuncs.custom_function_dialogue()

def tools_assisted_trendline(menu):
    set_current_user_input(ChartTools.AssistedTrendline())

def tools_andrews_pitch_fork(menu):
    set_current_user_input(ChartTools.AndrewsPitchFork())

def adjust_interval(widget):
    cc = current_chart.get_current()
    if cc:
        v = int(widget.value)
        if v > 0:
            v -= 1
        cc.set_start_bar(v)
        schedule_redraw()


############################################################################
# Format menu options:
# Pupose is to allow the user to format indicators seperate from a chart
# because generally indicators are thought to be seperate from charts. Within
# this implement there is very little difference, but to make use of the
# software easier we provide the obvious menu options.
# The Data Set and Drawables menu provide an interface that maps into the
# implementation of the software. These menus should provide more flexibiliy
# at the cost of on not being obvious at first.

# format_drawables
# display a list of drawables in the current chart.
# - the chart asks each subchart of a list of it's drawables.
#   Each drawable should have a unique name. The chart should return a list
#   of truples made up of (drawable name, ref to drawable instance).
# User selects a drawable.
# The drawables change_properties method is called. Control is then
# to the drawble. It is expected that the drawable will get a reference to
# the current parent window.
# The return value from the drawable's change_properties is to be one if the
# user selected OK or -1 if the user selected cancel.
def format_drawables():
    pass

# format_indicators is similar to format_drawables except that only
# indicators are displayed in the list. Thinking about the previous sentence
# means that the format_drawables, format_indicators and format_chart
# functions will probably use a subset of functionality which should make
# writing these functions easier.
def format_indicators():
    pass

# format_dataset
# what properties of a dataset could you change? Deleting is always an option,
# but other than that? Not sure if this menu item will last. Certainly create
# is needed.
def format_dataset():
    pass

# format_chart
def format_chart(_menu):
    scale, extrabars = dialogues.format_chart_dialogue(None)
    if scale == 'Weekly':
        scale_chart_weekly(_menu)
    elif scale == 'Daily':
        scale_chart_daily(_menu)
    elif scale == 'Monthly':
        scale_chart_monthly(_menu)
    else:
        print  "Bad scale value in format_chart ", scale
    
#############################################################################
# New

# The new functions just create the selected types.
#
# Each function is going to have some prerequisites. This need to be held in
# one place, with most likely in chase.py namespace.

# new_drawable: allows for the creation of a both chart type drawables and
# indicator type drawables.
def new_drawable():
    pass

# new_indicator: creates indicator type drawables only. The option should be
# given for the user to select 'create a new subchart' or 'display in existing
# subchart'. Default will depend upon the type of drawable. Each drawable
# should a preference behaviour, eg RSI would like to create a new subchart
# but an MA would want to stick itself on the subchart of the dataseries
# it was created on (which brings up an interesting point, how would it know
# which subchart the dataseries it is based upon, and so where to have itself
# drawn?. Right now there is no way for a drawable to indicate which subchart
# it's drawn on. The heirarchical layout of the chart->subchart->drawable is
# beginning to unravel as expected).
def new_indicator(win):
    # what to do?
    # display a list of indicators that can be created.
    # user selects an indicator.
    # dialogue is displayed with the condifurables for the indicator,
    # which includes catering for the use of non-standard datasets and
    # selecting drawing on a new or existing subchart. The default subchart
    # should be the one that the indicator selects, eg RSI would be a new
    # subchart, MA would be drawn in the same subchart as the dataseries from
    # which is was calculated (isn't that going to be fun?.
    # user configures the indicator
    # appropriate drawable is created with values
    # subchart created if needed.
    # drawabled to subchart.
    # subchart add to chart if needed.
    # chart redrawn.
    indicators = drawable.list_available_indicators()
    selected = dialogues.selection_dialogue(win, 'Select Indicator',
                                            indicators)
    if selected == None:  # cancel button pushed
        return
    d = drawable.new_drawable_from_name(selected)
    cc = current_chart.get_current()
    dataseries_list = cc.dsget_headers()
    subchart_list = cc.list_subcharts()
    d.change_properties(dataseries_list, subchart_list)

# new_chart: creates another empty chart adding it the list of charts held
# in chase.py. The new chart is set as the current chart, and is blank.
# There should be the option to copy an existing chart including the dataset,
# subcharts and drawables. All of this copy would have to be deep copying as
# changes to one should not effect another.
def new_chart():
    pass

# new_subchart: create an empty subchart in the position of the users choice.
# the default position will be the bottom (closest to the bottom of the
# screen). Allowing the user to select, means that the user can insert a
# subchart and so drawables if desired.
def new_subchart():
    pass

#############################################################################
# Functions for changing the X scale of a chart

def scale_chart_daily(menu):
    cc = current_chart.get_current()
    if cc != None:
        cc.set_chart_scale_daily()
        set_scroller_values(cc.get_total_bars(), cc.get_numbars())
        schedule_redraw()
        
def scale_chart_weekly(menu):
    cc = current_chart.get_current()
    if cc != None:
        cc.set_chart_scale_weekly()
        set_scroller_values(cc.get_total_bars(), cc.get_numbars())
        schedule_redraw()

def scale_chart_monthly(menu):
    cc = current_chart.get_current()
    if cc != None:
        cc.set_chart_scale_monthly()
        set_scroller_values(cc.get_total_bars(), cc.get_numbars())
        schedule_redraw()



def create_menu_bar(win):
    mf = GtkExtra.MenuFactory()
    mf.add_entries(menu_bar_array)
    win.add_accel_group(mf.accelerator)
    mf.show()
    return mf

##############################################################################
# auto loading of charts. This might disappear once the saving of state
# code has been written.

def do_autoload():
    if not chase_options.has_key(AUTOLOAD_LIST):
        return None
    stock_list = []
    stock_list = parse_autoload_options(chase_options[AUTOLOAD_LIST])
    directory = ""
    filename = ""
    try:
        directory = chase_options[STOCK_DIR]
    except:
        directory = ""
    for s in stock_list:
        filename = directory + s
        auto_file_load(filename)
    make_chart_current(stock_list[0])

# the parse_autoload_options function should be called *after* the main window
# is up and allocated.
def parse_autoload_options(str):
    stocks = []
    stocks = string.split(str, ',')
    return stocks

##############################################################################

def set_option(name, value):
    name.lower()
    chase_options[name] = value

def get_option(name):
    name.lower()
    if chase_options.has_key(name):
        return chase_options[name]
    else:
        return None

def load_rc_file():
    if os.environ.has_key(RC_FILE):
        loc = os.environ[RC_FILE]
    else:
        loc = get_option(RC_FILE)
        if loc == None:
            if os.environ.has_key('HOME'):
                loc = os.environ['HOME']
                loc += '/' + RC_FILE_NAME
    try:
        rcfile = open(loc)
    except Exception, e:
        sys.stderr.write("Couldn't read .chase_rc file: %s\n" % (e,))
        return None

    rcfile_patt = re.compile(RC_FILE_PAT)
    base_patt = re.compile(BASE_PAT)
    stockdir_patt = re.compile(STOCK_DIR_PAT)
    autoload_patt = re.compile(AUTOLOAD_PAT)
    realtime_patt = re.compile(REALTIME_PAT)
    line_num = 0
    for line in rcfile.readlines():
        line_num += 1
        # should really re-work this bit. Obviously there is common code that
        # could be cleaned up.
        m = rcfile_patt.match(line)
        if m != None:
            if m.group(3) == None:
                sys.stderr.write("Bad formed line at %d\n" % (line_num,))
            else:
                set_option(RC_FILE, m.group(3))
            continue
        m = base_patt.match(line)
        if m != None:
            if m.group(3) == None:
                sys.stderr.write("Bad formed line at %d\n" % (line_num,))
            else:
                set_option(CHASE_BASE, m.group(3))
        m = stockdir_patt.match(line)
        if m != None:
            if m.group(3) == None:
                sys.stderr.write("Bad formed line at %d\n" % (line_num,))
            else:
                set_option(STOCK_DIR, m.group(3))
        m = autoload_patt.match(line)
        if m != None:
            if m.group(3) == None:
                sys.stderr.write("Bad formed line at %d\n" % (line_num,))
            else:
                set_option(AUTOLOAD_LIST, m.group(3))
        m = realtime_patt.match(line)
        if m != None:
            if m.group(3) == None:
                sys.stderr.write("Bad formed line at %d\n" % (line_num,))
            else:
                add_realtime_entry(m.group(3))
        if line == "\n":
            continue
                

# since glade is being used to design the dialogues, loading the xml into
# memory is now needed.
def load_glade_dialogues():
    fileloc = ''
    if os.environ.has_key(CHASE_BASE):
        fileloc = sys.environ(CHASE_BASE)
    else:
        fileloc = get_option(CHASE_BASE)
        if fileloc == None:
            # put up a message box saying that there is no chase_base setup
            # and exit.
            sys.stderr.write("Could find CHASE_BASE variable in rc file\n")
            sys.exit(1)
    try:
        chase_glade_class = libglade.GladeXML(fileloc)
    except Exception, e:
        sys.stderr.write("Failed to load XML dialogues: %s\n" % (e,))
        sys.exit(1)
        

def parse_command_line():
    if len(sys.argv) == 1:
        return 1
    try:
        args = getopt.getopt(sys.argv[1:], 'b:')
    except:
        pass
    for i in range(0, len(args)):
        if not args[i]:
            break
        opt, values = args[i][0]
        if opt == '-b':
            set_option('CHASE_BASE', value)
        if opt == '-f':
            set_option('RC_FILE', value)

## Button handling functions.
def left_end_button_click(button):
    cc = current_chart.get_current()
    if cc:
        if cc.get_start_bar() != 0:
            adjust = Gtk_values['scroller']
            adjust.set_value(0)
            schedule_redraw()
    
def left_one_bar_button_click(button):
    cc = current_chart.get_current()
    if cc:
        cstart_bar = cc.get_start_bar() -1
        if cstart_bar > 0:
            adjust = Gtk_values['scroller']
            adjust.set_value(cstart_bar)
            schedule_redraw()
            
def right_one_bar_button_click(button):
    cc = current_chart.get_current()
    if cc:
        startbar = cc.get_start_bar()
        if startbar + cc.get_numbars() < cc.get_total_bars():
            newstartbar = startbar +1
            cc.set_start_bar(newstartbar)
            adjust = Gtk_values['scroller']
            adjust.set_value(newstartbar)
            schedule_redraw()

def right_end_button_click(button):
    cc = current_chart.get_current()
    if cc:
        nb = cc.get_numbars()
        tb = cc.get_total_bars()
        adjust = Gtk_values['scroller']
        adjust.set_value(tb - nb+1 )
        schedule_redraw()
    
def set_anchor_button_click(button):
    schedule_redraw()
    
def anchor_plus_one_button_click(button):
    schedule_redraw()
    
def less_bars_button_click(button):
    cc = current_chart.get_current()
    if cc:
        (sb, nb) = (0, 0)
        nb_pre = cc.get_numbars()
        sb_pre = cc.get_start_bar()
        if nb_pre  > 50:
            # move to the left by the amoun that the numbars shrinks
            nb = nb_pre - 50
            sb = sb_pre + 50   
            cc.set_numbars(nb)
            cc.set_start_bar(sb)
            set_scroller_values(cc.get_total_bars(), nb)
            adjust = Gtk_values['scroller']
            adjust.set_value(sb)
            schedule_redraw()
    
def more_bars_button_click(button):
    cc = current_chart.get_current()
    if cc:
        adjust = Gtk_values['scroller']
        sb_pre = cc.get_start_bar()
        nb_pre = cc.get_numbars()
        tb = cc.get_total_bars()
        nb = nb_pre + 50
        # handle the sit. where the number of bars to be displayed is greater
        # than the number of bars loaded.
        if nb > tb: 
            nb = tb
            sb = 0
        else:
            if sb_pre < 50:
                sb = sb_pre
            else:
                sb = sb_pre - 50
        cc.set_start_bar(sb)
        cc.set_numbars(nb)
        #adjust.set_all(sb, 0, cc.get_total_bars(), 1, nb, nb)
        set_scroller_values(cc.get_total_bars(), nb)
        adjust = Gtk_values['scroller']
        adjust.set_value(sb)
        schedule_redraw()

def make_chart_current(chart_name):
    if chart_name != current_chart.get_current_name():
        current_chart.set_current(chart_name)
        cc = current_chart.get_current()
        nb= cc.get_numbars()
        tb= cc.get_total_bars()
        sb= cc.get_start_bar()
        set_scroller_values(tb, nb)
        adjust= Gtk_values['scroller']
        adjust.set_value(sb)
        Gtk_values['win'].set_title(chart_name)
        schedule_redraw()

def charts_selection(_menu, chart_name):
    make_chart_current(chart_name)

def charts_menu_placement_func(menu, x, y):
    swidth = screen_width()
    sheight = screen_height()
    width, height = charts_menu_placement_func.popup.size_request()
    x,y,w,h = charts_menu_placement_func.button.get_allocation()
    return (x,y+100)

def charts_button_click(button):
    accelerator= GtkAccelGroup()
    popup= GtkMenu()
    popup.set_accel_group(accelerator)
    c = current_chart.get_all()
    c.sort()
    for i in c:
        p = GtkMenuItem(label=i)
        p.show()
        p.connect("activate", charts_selection, i)
        popup.append(p)
    popup.popup(None, None, None, 1, 1)

def setup():
    # expect parse_command_line to exit if there is a prompt with the command
    # line options.
    parse_command_line()
    load_rc_file()
    win = GtkWindow(type=WINDOW_TOPLEVEL)
    Gtk_values['win'] = win
    win.connect("delete_event", delete_cb)
    win.set_title("Chase")
    win.set_usize(500, 600)
    win.add_events(GDK.ALL_EVENTS_MASK)

    
    dialogues.parent_window = win
    
    vbox = GtkVBox(0, 0) # what does 0, 0 do?
    win.add(vbox)
    vbox.show()

    menu_bar = create_menu_bar(win)
    vbox.pack_start(menu_bar, expand=FALSE)
    menu_bar.show()

    tool_bar_hbox = GtkHBox()
    tool_bar_hbox.show()
    vbox.pack_start(tool_bar_hbox, expand=FALSE)

    left_end = GtkButton('Far Left')
    left_end.show()
    left_end.connect('clicked', left_end_button_click)
    tool_bar_hbox.pack_start(left_end, expand=FALSE)
    
    right_end_button = GtkButton('Far Right')
    right_end_button.show()
    right_end_button.connect('clicked', right_end_button_click)
    tool_bar_hbox.pack_start(right_end_button, expand=FALSE)
    
    more_bars = GtkButton('More Bars')
    more_bars.connect('clicked', more_bars_button_click)
    more_bars.show()
    tool_bar_hbox.pack_start(more_bars, expand=FALSE)

    less_bars = GtkButton('Less Bars')
    less_bars.connect('clicked', less_bars_button_click)
    less_bars.show()
    tool_bar_hbox.pack_start(less_bars, expand=FALSE)

    charts = GtkButton("Charts")
    charts.connect('clicked', charts_button_click)
    charts.show()
    tool_bar_hbox.pack_start(charts, expand=FALSE)
    
    drawing_area = GtkDrawingArea()
    vbox.pack_start(drawing_area)
    Gtk_values['da'] = drawing_area
    drawing_area.connect("expose_event", expose_cb)
    drawing_area.connect("configure_event", configure_cb)
    drawing_area.connect("motion_notify_event", motion_notify_cb)    
    drawing_area.connect("button_press_event", button_press_cb)
    drawing_area.connect("button_release_event", button_release_cb)
    drawing_area.add_events(GDK.BUTTON_PRESS_MASK)
    drawing_area.add_events(GDK.POINTER_MOTION_MASK)
    drawing_area.show()

    scroller_adjust = GtkAdjustment(0,0,0,0,0,0)
    hscroll_bar = GtkHScrollbar(scroller_adjust)
    hscroll_bar.set_update_policy(UPDATE_CONTINUOUS)
    scroller_adjust.connect("value_changed", adjust_interval)
    vbox.pack_start(hscroll_bar, 0, 0, 0)
    Gtk_values['scroller'] = scroller_adjust
    Gtk_values['hscroll_bar'] = hscroll_bar

    win.show()
    do_autoload()

###################################################################
## debugging

def debug_redraw_screen_black(menu):
    p = Gtk_values['primary_pixmap']
    w = Gtk_values['da']
    #draw_rectangle(p, w.get_style().black_gc, TRUE, 0, 0,
    #               w.get_window().width, w.get_window().height)
    #cc = current_chart.get_current()
    schedule_redraw()
    w.queue_draw()

def debug_dump_drawables(menu):
    print
    cc = current_chart.get_current()
    for i in cc.subchart.keys():
        for x in cc.subchart[i].drawables.keys():
            print x

def debug_dump_charts(menu):
    for i in current_chart.get_all(): print i


##############################################################################
# this is the array that is the menu bar.
# having it reference by the menu_bar_array variable means that it can be
# changed before calling the create_menu_bar function.

menu_bar_array = [
        ('File/Open', '<control>O', file_open),
        ('File/Close', '<control>C', file_close),
        #('File/Save', '<control>S', file_save),
        ('File/Reload', '<control>R', file_reload),
        ('File/Exit', '<control>X', file_exit),
        ('Tools/Cross Hairs', None, tools_cross_hairs),
        ('Tools/Horizontal Line', None, tools_hline),
        ('Tools/Vertical Line', None, tools_vline),
        ('Tools/Trend Line', None, tools_tline),
        ('Tools/Custom Function', None, tools_custfuncs),
        ('Tools/Assisted Trendline', None, tools_assisted_trendline),
        ('Tools/Andrew\'s PitchFork', None, tools_andrews_pitch_fork),
        #('New/Indictator', None, new_indicator),
        #('New/Chart', None, new_chart),
        #('New/Drawable', None, new_drawable),
        #('New/Subchart', None, new_subchart),
        #('Format/Indicators', None, format_indicators),
        ('Format/Chart', None, format_chart),
        #('Format/Drawables', None, format_drawables),
        #('Format/Data Set', None, format_dataset),
        ('Debug/Re-draw screen black', None, debug_redraw_screen_black),
        ('Debug/Dump drawables', None, debug_dump_drawables),
        ('Debug/Dump charts', None, debug_dump_charts)
        ]

##############################################################################
# realtime loading, variables and stuff.

def add_realtime_entry(l):
    global menu_bar_array
    entry_name, entry_script = string.split(l, ',')
    if os.access(entry_script, os.R_OK | os.X_OK):
        real_time_entries[entry_name]= entry_script
        menu_bar_array.append(('File/Real Time/'+entry_name, None,
                               file_realtime_update, entry_name))
    else:
        sys.stderr.write("Bad values given as realtime entry: %s" \
                         % (entry_name,))

###################################################################
    
if __name__ == '__main__':
    setup()
    try:
        mainloop()
    except:
        sys.stderr.write("Uncaught expection\n")
        sys.exit(1)
