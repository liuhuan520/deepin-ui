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

from box import EventBox
from constant import DEFAULT_FONT_SIZE, BUTTON_PRESS, BUTTON_NORMAL, BUTTON_HOVER
from draw import draw_vlinear, draw_pixbuf, draw_text, expose_linear_background
from theme import ui_theme
from utils import get_content_size, propagate_expose
import gobject
import gtk

class Categorybar(EventBox):
    '''
    Categorybar.
    '''
	
    def __init__(self, 
                 items, 
                 font_size=DEFAULT_FONT_SIZE, 
                 padding_left=20, 
                 padding_middle=10, 
                 padding_right=25):
        '''
        Initialize Categorybar class.
        
        @param items: A list of category item, format: (icon_dpixbuf, content, click_callback)
        '''
        # Init event box.
        super(Categorybar, self).__init__()
        self.category_index = 0
        self.connect(
            "expose-event",
            lambda w, e:
                expose_linear_background(w, e, ui_theme.get_shadow_color("categorybar_background").get_color_info()))
        
        # Init category box.
        self.category_item_box = gtk.VBox()
        self.add(self.category_item_box)
        
        # Init item.
        if items:
            icon_width = self.get_icon_width(items)
            for (index, item) in enumerate(items):
                category_item = CategoryItem(item, index, font_size, icon_width, padding_left, padding_middle, padding_right,
                                 self.set_index, self.get_index)
                self.category_item_box.pack_start(category_item)
                
        # Show.
        self.show_all()        
        
    def set_index(self, index):
        '''
        Set selected item index.
        
        @param index: Index of selected item.
        '''
        self.category_item_box.queue_draw()
        self.category_index = index
        
    def get_index(self):
        '''
        Get selected index.
        
        @return: Return selected item index.
        '''
        return self.category_index
        
    def get_icon_width(self, items):
        '''
        Get icon width.
        
        @param items: A list of category item, format: (icon_dpixbuf, content, click_callback)
        '''
        icon_width = 0
        for (icon_dpixbuf, content, _) in items:
            if icon_dpixbuf:
                icon_width = icon_dpixbuf.get_pixbuf().get_width()
                break
            
        return icon_width    
    
gobject.type_register(Categorybar)    
    
class CategoryItem(gtk.Button):
    '''
    CategoryItem class for use in CategoryBar.
    
    @undocumented: wrap_category_item_clicked_action
    @undocumented: expose_category_item
    '''    
	
    def __init__(self, 
                 item, 
                 index, 
                 font_size, 
                 icon_width, 
                 padding_left, 
                 padding_middle, 
                 padding_right, 
                 set_index, 
                 get_index):
        '''
        Initialize CategoryItem class.
        
        @param item: Category item, format: (item_dpixbuf, content, click_callback)
        @param index: Category item index.
        @param font_size: Font size.
        @param icon_width: Icon width.
        @param padding_left: Padding at left of item. 
        @param padding_middle: Padding between icon and font.
        @param padding_right: Padding at right of item.
        @param set_index: Set index callback.
        @param get_index: Get index callback.
        '''
        # Init.
        gtk.Button.__init__(self)
        self.font_size = font_size
        self.index = index
        self.set_index = set_index
        self.get_index = get_index
        self.padding_left = padding_left
        self.padding_right = padding_right
        (self.icon_dpixbuf, self.content, self.clicked_callback) = item
        (content_width, font_height) = get_content_size(self.content, self.font_size)
        
        # Init item button.
        self.font_offset = 0
        if icon_width == 0:
            self.font_offset = 0
        else:
            self.font_offset = padding_middle + icon_width
        self.set_size_request(
            padding_left + self.font_offset + content_width + padding_right,
            -1
            )

        self.connect("expose-event", self.expose_category_item)    
        self.connect("clicked", lambda w: self.wrap_category_item_clicked_action())

    def wrap_category_item_clicked_action(self):
        '''
        Internal function, wrap clicked action.
        '''
        if self.clicked_callback:
            self.clicked_callback()
        self.set_index(self.index)

    def expose_category_item(self, widget, event):
        '''
        Internal function, callback for `expose-event` signal.
        
        @param widget: Gtk.Widget instance.
        @param event: Expose event.
        @return: Always return True.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        select_index = self.get_index()
        font_color = ui_theme.get_color("category_item").get_color()
        
        # Draw background.
        if widget.state == gtk.STATE_NORMAL:
            if select_index == self.index:
                select_status = BUTTON_PRESS
            else:
                select_status = BUTTON_NORMAL
        elif widget.state == gtk.STATE_PRELIGHT:
            if select_index == self.index:
                select_status = BUTTON_PRESS
            else:
                select_status = BUTTON_HOVER
        elif widget.state == gtk.STATE_ACTIVE:
            select_status = BUTTON_PRESS
            
        if select_status == BUTTON_PRESS:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height, 
                        ui_theme.get_shadow_color("category_item_press").get_color_info())
    
            font_color = ui_theme.get_color("category_select_item").get_color()
        elif select_status == BUTTON_HOVER:
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height, 
                        ui_theme.get_shadow_color("category_item_hover").get_color_info())
            
            font_color = ui_theme.get_color("category_select_item").get_color()
            
        # Draw navigate item.
        category_item_pixbuf = self.icon_dpixbuf.get_pixbuf()
        draw_pixbuf(
            cr, category_item_pixbuf, 
            rect.x + self.padding_left,
            rect.y + (rect.height - category_item_pixbuf.get_height()) / 2
            )
        
        # Draw font.
        draw_text(cr, self.content, 
                    rect.x + self.padding_left + self.font_offset,
                    rect.y,
                    rect.width - self.padding_left - self.font_offset - self.padding_right,
                    rect.height,
                    self.font_size, 
                    font_color,
                    )
        
        # Propagate expose to children.
        propagate_expose(widget, event)
    
        return True
    
gobject.type_register(CategoryItem)
