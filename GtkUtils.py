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


## Code to help out with gtk stuff.

import gtk

def build_popup_menu(drawable_instance, activate_callback, \
                     build_function,
                     parent_menu, *menu_list):
    for m in menu_list[0]:
        apply(build_function, [drawable_instance, activate_callback, \
                               parent_menu, m])

def build_sub_popup_menu(drawable_instance, activate_callback, \
                         parent_menu, colour):
    parent_menu.add(make_popup_menu_item(drawable_instance, activate_callback,\
                                         colour))

def make_popup_menu_item(drawable_instance, activate_callback, colour):
    colourobj= eval(("gtk.GtkMenuItem(label=\"%s\")") % (colour),)
    colourobj.show()
    colourobj.connect("activate", \
                      eval("drawable_instance.%s_%s" % \
                           (activate_callback, colour)))
    return colourobj
