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


# Class to encapsulate the handling of events for various user driven
# drawing and price selection. Right (23/12/2002) there is a both of
# if/else statements stuck in chase.py for each of the window event callbacks.
# The goal is to put that functionality into a class and store state in that
# class also. Basically looking to clean up and refactor.

# Dummy class used it EventHandlerInterface is instastiated.
class InterfaceOnly(Exception): pass

# don't try and instantiate this class.
class EventHandlerInterface:
    def __init__(self):
        raise InterfaceOnly

    def configure_cb(self, win, event):
        return None

    def delete_cb(self, win, event):
        return None

    def expose_cb(self, win, event):
        return None

    def motion_notify_cb(self, win, event):
        return None

    def button_press_cb(self, win, event):
        return None

    def button_release_cb(self, win, event):
        return None
        
class EventHandlerNull:
    """The NULL event handler. This class exists so that code in the client
    doesn't have to check for an explicit NULL variable. """
    def __init__(self):
        pass
    
