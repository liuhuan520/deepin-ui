#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from constant import EDGE_DICT
import gtk
from utils import (resize_window, is_double_click, move_window)

class WindowBase(gtk.Window):
    '''
    Window base.
    '''
	
    def __init__(self,
                 window_type=gtk.WINDOW_TOPLEVEL, 
                 ):
        '''
        init docs
        '''
        gtk.Window.__init__(self, window_type)
        
    def show_window(self):
        """
        Show the window.
        """
        self.show_all()

    def toggle_max_window(self):
        """
        Toggle the window size between maximized size and normal size.
        """
        window_state = self.window.get_state()
        if window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.unmaximize()
        else:
            self.maximize()

    def toggle_fullscreen_window(self):
        """
        Toggle the window between fullscreen mode and normal size.
        """
        window_state = self.window.get_state()
        if window_state == gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.unfullscreen()
        else:
            self.fullscreen()
            
    def close_window(self):
        """
        Close the window. Send the destroy signal to the program.

        @return: Always return False.
        """
        # Hide window immediately when user click close button,
        # user will feeling this software very quick, ;p
        self.hide_all()

        self.emit("destroy")
    
        return False
        
    def min_window(self):
        """
        Minimize the window. Make it iconified.
        """
        self.iconify()
        
    def resize_window(self, widget, event):
        """
        Resize the window.

        @param widget: The window of type gtk.Widget.
        @param event: A signal of type gtk.gdk.Event.
        """
        if self.enable_resize:
            edge = self.get_edge()            
            if edge != None:
                resize_window(self, event, self, edge)
                
    def is_disable_window_maximized(self):
        """
        An interface which indicates whether the window could be maximized, you should implement this function you own.
        @return: Always return False.
        """
        return False                
                
    def monitor_window_state(self, widget, event):
        """
        Internal function to monitor window state, 

        add shadow when window at maximized or fullscreen status. Otherwise hide shadow.

        @param widget: The window of type gtk.Widget.
        @param event: The event of gtk.gdk.Event.
        """
        window_state = self.window.get_state()
        if window_state in [gtk.gdk.WINDOW_STATE_MAXIMIZED, gtk.gdk.WINDOW_STATE_FULLSCREEN]:
            self.hide_shadow()
            
            if self.is_disable_window_maximized():
                self.unmaximize()
        else:
            self.show_shadow()
        
    def add_move_event(self, widget):
        """
        Add move event callback.

        @param widget: A widget of type gtk.Widget.
        """
        widget.connect("button-press-event", lambda w, e: move_window(w, e, self))            
        
    def add_toggle_event(self, widget):
        """
        Add toggle event callback.

        @param widget: A widget of type gtk.Widget.
        """
        widget.connect("button-press-event", self.double_click_window)        
        
    def double_click_window(self, widget, event):
        """
        Double click event handler of the window. It will maximize the window.

        @param widget: A widget of type gtk.Widget.
        @param event: A event of type gtk.gdk.Event.
        @return: Always return False.
        """
        if is_double_click(event):
            self.toggle_max_window()
            
        return False    
            
    def get_edge(self):
        """
        Get the edge which the cursor is on, according to the cursor type.

        @return: If there is a corresponding cursor type, an instance of gtk.gdk.WindowEdge is returned, else None is returned.
        """
        if EDGE_DICT.has_key(self.cursor_type):
            return EDGE_DICT[self.cursor_type]
        else:
            return None

    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface, you should implement this function own.
        
        @param cr: Cairo context.
        @param x: X coordinate of draw area.
        @param y: Y coordinate of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        pass
    
    def get_cursor_type_with_coordinate(self, ex, ey, wx, wy, ww, wh):
        if wx <= ex <= wx + self.shadow_padding:
            if wy <= ey <= wy + self.shadow_padding * 2:
                return gtk.gdk.TOP_LEFT_CORNER
            elif wy + wh - (self.shadow_padding * 2) <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_LEFT_CORNER
            elif wy + self.shadow_padding < ey < wy + wh - self.shadow_padding:
                return gtk.gdk.LEFT_SIDE
            else:
                return None
        elif wx + ww - self.shadow_padding <= ex <= wx + ww:
            if wy <= ey <= wy + self.shadow_padding * 2:
                return gtk.gdk.TOP_RIGHT_CORNER
            elif wy + wh - (self.shadow_padding * 2) <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_RIGHT_CORNER
            elif wy + self.shadow_padding < ey < wy + wh - self.shadow_padding:
                return gtk.gdk.RIGHT_SIDE
            else:
                return None
        elif wx + self.shadow_padding < ex < wx + ww - self.shadow_padding:
            if wy <= ey <= wy + self.shadow_padding:
                return gtk.gdk.TOP_SIDE
            elif wy + wh - self.shadow_padding <= ey <= wy + wh:
                return gtk.gdk.BOTTOM_SIDE
            else: 
                return None
        else:
            return None
    
