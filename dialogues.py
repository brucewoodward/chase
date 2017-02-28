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
import GtkExtra

parent_window = None

def set_our_parent_window(our_window):
    global parent_window
    if parent_window != None:
        our_window.set_parent_window(parent_window.get_window())


class _selection_dialogue(GtkDialog):
    selection = ''
    list = []
    def __init__(self, title, list):
        GtkDialog.__init__(self)
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)
        self.set_modal(1)
        self.list = list
        set_our_parent_window(self)

        scrolled_win = GtkScrolledWindow()
        scrolled_win.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.vbox.pack_start(scrolled_win)
        scrolled_win.show()

        sellist = GtkCList(cols=1)
        sellist.set_selection_mode(SELECTION_BROWSE)
        scrolled_win.add_with_viewport(sellist)
        sellist.connect("select_row", self.clist_select)
        sellist.show()
        
        for x in self.list:
            sellist.append([x])
        
        button_box = GtkHBox(spacing=10)
        self.vbox.pack_start(button_box, expand=FALSE)
        button_box.show()

        select_button = GtkButton("Select")
        select_button.connect("clicked", self.select_button, sellist)
        button_box.pack_start(select_button)
        select_button.show()

        cancel_button = GtkButton("Cancel")
        cancel_button.connect("clicked", self.cancel_button)
        button_box.pack_start(cancel_button)
        cancel_button.show()

        return None
        
    def quit(self, *args):
        self.hide()
        self.destroy()
        mainquit()

    def clist_select(self, _clist, r, c, event):
        self.selection = self.list[r]

    def select_button(self, _button, sellist):
        self.quit()

    def cancel_button(self, _button):
        self.quit

    def get_selected_value(self):
        return self.selection
        
def selection_dialogue(win, title, list):
    s = _selection_dialogue(title, list)
    # s is a GtkDialog object
    s.show()
    mainloop()
    return s.selection

#############################################################################
# called by the SMA and EMA class' configure method.
class _ma_configure_dialogue(GtkDialog):
    def __init__(self):
        GtkDialog.__init__(self)
        self.set_usize(200, 300)
        self.set_title("Configure Moving Average")
        self.set_modal(1)
        set_our_parent_window(self)
        
        frame1 = GtkFrame("Data Source")
        frame1.show()
        frame1.set_border_width(4)
        self.vbox.pack_start(frame1)

        combo2 = GtkCombo()
        combo2.show()
        frame1.add(combo2)
        
        entry1 = combo2.entry
        entry1.set_text('Select Data Series')
        entry1.show()

        hbox2 = GtkHBox()
        hbox2.show()
        hbox2.set_border_width(5)

        label5 = GtkLabel('Time Period')
        label5.show()
        hbox2.pack_start(label5, gtk.TRUE, gtk.TRUE, 0)

        spinbutton2_adj = GtkAdjustment(1, 0, 100, 1, 10, 10)
        spinbutton2 = GtkSpinButton(spinbutton2_adj, 1, 0)
        spinbutton2.show()
        hbox2.pack_start(spinbutton2, gtk.TRUE, gtk.TRUE, 0)

        frame2 = GtkFrame('Shift Moving Average')
        frame2.show()
        self.vbox.pack_start(frame2, gtk.TRUE, gtk.TRUE, 1)
        frame2.set_border_width(5)

        vbox2 = GtkVBox(FALSE, 5)
        vbox2.show()
        frame2.add(vbox2)
        vbox2.set_border_width(7)

        togglebutton3 = GtkToggleButton('Shift Moving Average')
        togglebutton3.show()
        vbox2.pack_start(togglebutton3, gtk.FALSE, gtk.FALSE, 0)

        togglebutton4 = GtkToggleButton('Shift Moving Average Left')
        togglebutton4.show()
        vbox2.pack_start(togglebutton4, gtk.FALSE, gtk.FALSE, 0)

        togglebutton5 = GtkToggleButton('Shift Moving Average Right')
        togglebutton5.show()
        vbox2.pack_start(togglebutton5, gtk.FALSE, gtk.FALSE, 0)

        hbox3 = GtkHBox(gtk.FALSE, 5)
        hbox3.show()
        vbox2.pack_start(hbox2, gtk.TRUE, gtk.TRUE, 0)
        hbox3.set_border_width(10)

        label6 = GtkLabel('Number of Bars to Shift')
        label6.show()
        hbox3.pack_start(label6, gtk.FALSE, gtk.FALSE, 0)

        spinbutton3_adj = GtkAdjustment(1,0,100,1,10,10)
        spinbutton3 = GtkSpinButton(spinbutton3_adk,1,0)
        spinbutton3.show()
        hbox3.pack_start(spinbutton3, gtk.TRUE, gtk.TRUE, 0)

        frame3 = GtkFrame('Select Subchart')
        frame3.show()
        self.vbox.pack_start(frame3, gtk.TRUE, gtk.TRUE, 0)
        frame3.set_border_width(5)

        combo1 = GtkCombo()
        combo1.show()
        frame3.add(combo1)
        combo1.set_border_width(10)

        combo_entry1 = combo1.entry
        combo_entry1.show()

        hbox1 = GtkHBox(gtk.TRUE, 0)
        
        
        
def ma_configure_dialogue(dataseries_list, subchart_list):
    """ returns
    1. the name of dataseries to use.
    2. Time Period as number of bars
    3. Shift direction (if any)
    4. Number of bars to shift if any.
    5. Name of the subchart to display in.
    """
    m = _ma_configure_dialogue(dataseries_list, subchart_list)
    m.show()
    mainloop()
    return None
    

##############################################################################
# Format -> Chart dialogue.

VALID_COMBO_ITEMS = ['Daily', 'Weekly', 'Monthly']

class _chart_format(GtkDialog):
    def __init__(self):
        self.selection = {'scale': None, 'extrabars': None} # values returned
        self.combo_entry = 0
        GtkDialog.__init__(self)
        set_our_parent_window(self)
        
        self.set_usize(235, 115)
        self.set_position(WIN_POS_CENTER)
        self.set_policy(TRUE, FALSE, FALSE)
        self.set_title('Chart Properties')
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)
        self.set_modal(1)

        hbox1 = GtkHBox(FALSE, 0)
        hbox1.show()
        self.vbox.pack_start(hbox1, FALSE, FALSE, 0)
        hbox1.set_border_width(5)

        label1 = GtkLabel(label="Scale")
        label1.show()
        hbox1.pack_start(label1, TRUE, TRUE, 0)

        self.combo1 = GtkCombo()
        self.combo1.show()
        hbox1.pack_start(self.combo1, TRUE, TRUE, 0)
        self.combo1.set_value_in_list(FALSE, FALSE)
        combo1_items = VALID_COMBO_ITEMS
        self.combo1.set_popdown_strings(combo1_items)

        self.combo_entry =self.combo1.entry
        self.combo_entry.show()
        self.combo_entry.set_text("Weekly")

        hbox2 = GtkHBox(FALSE, 0)
        hbox2.show()
        self.vbox.pack_start(hbox2, FALSE, FALSE, 0)
        hbox2.set_border_width(3)

        label2 = GtkLabel(label="Extra Bars")
        label2.show()
        hbox2.pack_start(label2, TRUE, TRUE, 0)

        spinbutton1_adj = GtkAdjustment(0, 0, 100, 1, 10, 10)
        self.spinbutton1 = GtkSpinButton(spinbutton1_adj)
        self.spinbutton1.show()
        hbox2.pack_start(self.spinbutton1, TRUE, TRUE, 0)

        hbox3 = GtkHBox(TRUE, 0)
        hbox3.show()
        self.action_area.pack_start(hbox3, FALSE, FALSE, 10)
        hbox3.set_border_width(5)

        ok_button = GtkButton(label="OK")
        ok_button.show()
        hbox3.pack_start(ok_button, TRUE, TRUE, 0)
        ok_button.set_border_width(5)
        ok_button.connect("clicked", self.ok_button)

        cancel_button = GtkButton(label="Cancel")
        cancel_button.show()
        hbox3.pack_start(cancel_button, TRUE, TRUE, 0)
        cancel_button.set_border_width(5)
        cancel_button.connect("clicked", self.cancel_button)

    def quit(self, *args):
        self.hide()
        mainquit()

    def cancel_button(self, _button):
        self.quit()

    def ok_button(self, _button):
        entry = self.combo1.entry.get_text()
        bars = self.spinbutton1.get_value_as_int()
        if bars < 0:
            bars = 0
        if entry not in VALID_COMBO_ITEMS:
            GtkExtra.message_box(title='Bad Value', message='Scale is invalid',
                                 buttons=('OK',), pixmap=None, modal=TRUE)
            self.selection['extrabars'] = None
            self.selection['scale'] = None
        else:
            self.selection['extrabars'] = bars
            self.selection['scale'] = entry
        self.quit()
        
            
def format_chart_dialogue(win):
    s = _chart_format()
    s.show()
    mainloop()
    return (s.selection['scale'], s.selection['extrabars'])

class _assisted_trendline_chose_point(GtkDialog):
    # expect drawables_names to a  list of the drawables that are on the
    # selected subchart.
    def __init__(self, drawables_names):
        GtkDialog.__init__(self)
        self.set_title("Select Point")
        self.set_modal(1)
        self.set_position(WIN_POS_CENTER)
        self.set_policy(TRUE, FALSE, FALSE)
        self.connect("destory", self.quit)
        self.connect("delete_event", self.quit)
        set_our_parent_window(self)
        
        self.checkboxes = {}
        self.cancelled = 0
        
        tmp_widget = None
        previousButton = None
        for d in drawables_names:
            tmp_widget = self.checkboxes[d] = \
                         GtkRadioButton(label=d, group=previousButton)
            previousButton= tmp_widget
            tmp_widget.show()
            tmp_widget.set_border_width(1)
            tmp_widget.set_active(FALSE)
            self.vbox.pack_start(tmp_widget, FALSE, FALSE, 0)
        self.checkboxes[drawables_names[0]].set_active(TRUE)

        butHBox = GtkHBox(FALSE,0)
        butHBox.show()
        self.action_area.pack_start(butHBox, FALSE, FALSE, 10)
        butHBox.set_border_width(3)
        
        ok_button = GtkButton(label="OK")
        ok_button.show()
        butHBox.pack_start(ok_button, TRUE, TRUE, 0)
        ok_button.connect('clicked',self.ok_button)

        cancel_button = GtkButton(label="Cancel")
        cancel_button.show()
        butHBox.pack_start(cancel_button, TRUE, TRUE, 0)
        cancel_button.connect('clicked',self.cancel_button)

    def quit(self, *args):
        self.hide()
        mainquit()

    def ok_button(self, _button):
        for i in self.checkboxes.keys():
            if self.checkboxes[i].get_active():
                self.selection = i
        self.quit()
        
    def cancel_button(self, _button):
        self.cancelled = 1
        self.quit()

def chose_point(drawables): # drawables is a list of the names of the drawables
    c = _assisted_trendline_chose_point(drawables)
    c.show()
    mainloop()
    if c.cancelled == 1:
        return "cancelled"
    else:
        return c.selection

