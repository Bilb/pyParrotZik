#!/usr/bin/env python

import sys
import re
import os

if sys.platform=="linux2" or sys.platform=="win32":
    import gtk
elif sys.platform=="darwin":
    import rumps


UPDATE_FREQUENCY = 30 # seconds

class SysIndicator:
    def __init__(self, icon,menu):
        if sys.platform=="linux2":
            self.menu = menu.gtk_menu
            import appindicator
            self.icon_directory = os.path.sep + 'usr' + os.path.sep+ 'share' + os.path.sep+'icons' + os.path.sep+'zik'+ os.path.sep
            self.statusicon = appindicator.Indicator("new-parrotzik-indicator",
                                           "indicator-messages",
                                           appindicator.CATEGORY_APPLICATION_STATUS)
            self.statusicon.set_status(appindicator.STATUS_ACTIVE)
            self.statusicon.set_icon_theme_path(self.icon_directory)
            self.statusicon.set_menu(self.menu)          
            
        elif sys.platform=="win32":  
            self.menu = menu.gtk_menu          
            self.icon_directory = os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep+ 'share' + os.path.sep+'icons' + os.path.sep+'zik'+ os.path.sep
            self.statusicon = gtk.StatusIcon()            
            self.statusicon.connect("popup-menu", self.gtk_right_click_event)
            self.statusicon.set_tooltip("Parrot Zik")
            self.menu_shown=False            
        
        self.setIcon(icon)

    def setIcon(self, name):
        if sys.platform=="linux2":
            self.statusicon.set_icon(name)
        elif sys.platform=="win32":
            self.statusicon.set_from_file(self.icon_directory+name+'.png') 

    def gtk_right_click_event(self, icon, button, time):
        import gtk
        if not self.menu_shown:
            self.menu_shown=True
            self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)
        else:
            self.menu_shown=False
            self.menu.popdown()

    def main(self):
        if sys.platform=="linux2" or sys.platform=="win32":
            gtk.main()       
        elif sys.platform=="darwin":
            self.app.run()

    def show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("Parrot Zik Tray")
        about_dialog.set_version("0.3")
        about_dialog.set_authors(["Dmitry Moiseev m0sia@m0sia.ru"])
        about_dialog.run()
        about_dialog.destroy()

    

class UniversalMenu:
    def __init__(self):
        if sys.platform=="linux2" or sys.platform=="win32":
            self.gtk_menu = gtk.Menu()
            self.gtk_quite_item = MenuItem("Quit",sys.exit).gtk_item
            self.gtk_menu.append(self.gtk_quite_item)

    def append(self,MenuItem):
        if sys.platform=="linux2" or sys.platform=="win32":
            self.gtk_menu.remove(self.gtk_quite_item)
            self.gtk_menu.append(MenuItem.gtk_item)
            self.gtk_menu.append(self.gtk_quite_item)

class MenuItem:
    def __init__(self,name,action,sensitive = True, checkitem = False):
        if sys.platform=="linux2" or sys.platform=="win32":
            if checkitem:
                self.gtk_item=gtk.CheckMenuItem(name) 
            else:
                self.gtk_item=gtk.MenuItem(name) 
            self.gtk_item.show()
            if action:
                self.gtk_item.connect("activate", action)

            if not sensitive:
                self.set_sensitive(sensitive)

    def set_sensitive(self,option):
        if sys.platform=="linux2" or sys.platform=="win32":
            return self.gtk_item.set_sensitive(option)

    def set_active(self,option):
        if sys.platform=="linux2" or sys.platform=="win32":
            return self.gtk_item.set_active(option)

    def get_active(self):
        if sys.platform=="linux2" or sys.platform=="win32":
            return self.gtk_item.get_active()

    def set_label(self,option):
        if sys.platform=="linux2" or sys.platform=="win32":
            return self.gtk_item.set_label(option)
