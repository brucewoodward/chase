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

# This modules provide a mechanism for drawables to be able to pass
# state/information back up to chase.py and have this information/state
# affect the UI of chase.

# It is intended that there will be a function for each purpose, so
# if the popup_menu of the trendline drawable has to tell chase that it
# should run the parrallel trendline class from the ChartTools modules
# there will be a specific function to do this.
# The reason for implementing this way is so that the drawables can get
# away with knowing nothing of chase's internals. All the mess is hidden
# away in here.

Command= ""

def get_loopback_command():
    """This function is called by chase.py. If there is a command to be
    executed then this function will return the appropriate class
    instance"""
    global Command
    return Command

def reset_loopback_command():
    global Command
    Command= ""

def parrallel_line_from_trendline_drawables(trendline):
    """Tell chase to start the class that draws parrallel lines, using
    trendline as the base for any information needed"""
    global Command
    Command= "current_user_input = ChartTools.ParrallelTrendlineFromExisting(%f)" % trendline.get_gradient()
