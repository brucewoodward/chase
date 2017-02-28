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

import os, sys, string, glob, GtkExtra

# functions are stored in a hash. The key is the name of the function and
# the value is the function itself.
function_list = {}

# Store a reference to the top level window.
Window = None
List = None

def _make_path():
    if os.environ['HOME']:
        return os.environ['HOME'] + '/.chase_functions'
    else:
        return nil

# open file using the editor specified in the options file. Probably need to
# add this information into the options setup for chase.
def run_editor_on(file):
    pass

# load up all of the custom functions in the proper directory.
# the customer functions dialogue will display the functions loaded. Don't
# edit the functions while chase is running except via edit button on the
# custom functions dialogue.
def load_functions():
    global List
    # right now we are going to assume that this code is only ever run on UNIX
    if 'HOME' in os.environ:
        path = _make_path()
        if os.access(path, os.F_OK & os.R_OK & os.X_OK):
            os.chdir(path)
            for f in glob.glob('*'):
                file = open(f)
                lines = file.readlines()
                function_list[f] = lines # don't think that this is right.
                file.close()
            return 1
        else:
            GtkExtra.message_box(title='Loading Error',
                                 message='Could read the file',
                                 buttons=('OK',))
            return 0
    else:
        # popup a message box saying that there wasn't anything
        # in the file.
        GtkExtra.message_box(title='Loading Error',
                             message='Environment is not configure. Can\'t HOME environment variable.',
                             buttons=('OK',))
    return 0

def new_button(_b):
    # popup little dialog to get the title of the function.
    # if user enters a name, start the editor so that the new function can be
    # edited.
    name = GtkExtra.input_box(title="Enter Function Name",
                              message="Name of the new function is? ",
                              modal=TRUE)
    if function_list.has_key(name):
        GtkExtra.message_box(title="Duplicate Function Name",
                             message="Function name already exists",
                             buttons=("OK"),
                             pixmap=None,
                             modal=TRUE)
    else:
        run_editor_on(_make_path() + '/' + name)

def run_button(_b):
    global List
    selection = List.get_selection()
    # compile the function.
    # prepare the environment to be sent to the function.
    # run the function with prepared in environment.
    #
    # need to be able to dump the output of the compile to a file for debugging
    # file name is '/tmp/chase_funcs.log'. Always append to this file.
    # Trimming the file size is the responsibility of the user.
    return 0

def delete_button(_b):
    global List
    selection = List.get_selection()

def edit_button(_b):
    global List

def close_button(_b):
    global Window
    global List 
    print List
    if List:
        s = List.get_selection()
        if len(s) == 0:
            print "get_selection returned None"
        else:
            print s
    Window.destroy()

def custom_function_dialogue():
    global Window
    global List

    list2 = GtkList()
    if load_functions():
        for x in function_list.keys():
            list_item = GtkListItem(x)
            list_item.show()
            list2.add(list_item)
    else:
        return 0
    
    win = GtkWindow(WINDOW_DIALOG)
    win.set_title('Custom Functions')
    win.set_usize(300, 300)
    win.set_modal(TRUE)
    Window = win
    
    table1 = GtkTable(3, 2, FALSE)
    table1.show()
    win.add(table1)

    frame3 = GtkFrame(label="Custom Functions")
    frame3.show()
    table1.attach(frame3, 0, 1, 0, 1, EXPAND | FILL, EXPAND | FILL, 0, 0)
    frame3.set_border_width(5)

    scrolledwindow3 = GtkScrolledWindow()
    frame3.add(scrolledwindow3)
    scrolledwindow3.show()

    viewport2 = GtkViewport()
    viewport2.show()
    scrolledwindow3.add(viewport2)


    list2.show()
    viewport2.add(list2)
    List = list2
    
    frame4 = GtkFrame(label="Function Details")
    frame4.show()
    table1.attach(frame4, 0, 1, 1, 2, FILL, EXPAND | FILL, 0, 0)
    frame4.set_border_width(5)

    scrolledwindow4 = GtkScrolledWindow()
    scrolledwindow4.show()
    frame4.add(scrolledwindow4)

    text2 = GtkText()
    text2.show()
    scrolledwindow4.add(text2)
    text2.set_line_wrap(TRUE)
    #text2.set_editable(TRUE)

    hbox3 = GtkHBox()
    hbox3.show()
    table1.attach(hbox3, 0, 1, 2, 3, 0, 0, 0, 0)

    button8 = GtkButton(label='Close')
    button8.show()
    button8.set_border_width(5)
    hbox3.add(button8)
    button8.connect('clicked', close_button)

    vbox3 = GtkVBox()
    vbox3.show()
    table1.attach(vbox3, 1, 2, 0, 1, 0, EXPAND | FILL, 0, 0)

    button10 = GtkButton(label='New')
    vbox3.add(button10)
    button10.show()
    button10.set_border_width(5)
    button10.connect('clicked', new_button)

    button11 = GtkButton(label='Run')
    vbox3.add(button11)
    button11.show()
    button11.set_border_width(5)
    button11.connect('clicked', run_button)

    button12 = GtkButton(label='Delete')
    vbox3.add(button12)
    button12.show()
    button12.set_border_width(5)
    button12.connect('clicked', delete_button)

    button13 = GtkButton(label='Edit')
    vbox3.add(button13)
    button13.show()
    button13.set_border_width(5)
    button13.connect('clicked', edit_button)

    win.show()
