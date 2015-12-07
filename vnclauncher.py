# Copyright (C) 2007, Eduardo Silva <edsiper@gmail.com>.
# Copyright (C) 2008, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

import logging
from gettext import gettext as _

import gtk
import dbus

from sugar.activity import activity
from sugar import env
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.palette import Palette
from sugar.graphics.roundbox import CanvasRoundBox
import ConfigParser
import os
import os.path
import vte
import pango
import commands
import sys
import platform
import logging

class VncLauncherActivity(activity.Activity):

    def _ipaddr_(self,button):
        ifconfig="/sbin/ifconfig"
        ifaces=['eth0','msh0']
        for iface in ifaces:
            cmd="%s %s" % (ifconfig, iface)
            output=commands.getoutput(cmd)
            ipaddr="Error!!"
            error="Error!! check wireless connection"
            inet = output.find('inet')
            if inet >= 0:
                print iface
                start=inet + len('inet')
                end=output.find(" ",start + 1)
                if iface == 'eth0':
                    ipaddr='Ethernet IP= '+ output[start:end]
                else:
                    ipaddr='Mesh IP='+ output[start:end]
                break
            else:
                ipaddr=error

        button.set_label('Please Click to find current IP address \n\n' +
                         ipaddr)

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        
        logging.debug('Starting the X11 VNC activity')
        
        self.set_title(_('X11 VNC Server Activity'))
        self.connect('key-press-event', self.__key_press_cb)
        args="Please Click to find current IP address"
        box = gtk.HBox(False, 10)
        table=gtk.Table(4,1,True)
        button=gtk.Button(args)
        button.connect("clicked",self._ipaddr_)
        table.attach(button,0,1,0,1,gtk.FILL|gtk.EXPAND,gtk.EXPAND|gtk.FILL,25,25)
        button.show()
        button=gtk.Button("Start X11 VNC Server")
        button.connect("clicked",self.connectVNC)
        table.attach(button,0,1,1,2,gtk.FILL|gtk.EXPAND,gtk.FILL|gtk.EXPAND,25,25)
        button.show()
        
        button=gtk.Button("Stop X11 VNC Server")
        button.connect("clicked",self.stopVNC)
        table.attach(button,0,1,2,3,gtk.FILL,gtk.FILL,25,25)
        button.show()

        button=gtk.Button("Exit VncLauncherActivity")
        button.connect("clicked",lambda w:gtk.main_quit())
        table.attach(button,0,1,3,4,gtk.FILL,gtk.FILL,25,25)
        button.show()
        table.show()
         
        self._vte = VTE()
        self._vte.show()

        box.pack_start(self._vte)
        box.pack_start(table, False, False, 0)
        
        self.set_canvas(box) 
        box.show()

    def stopVNC(self,button):
	
        cmd = "kill" + commands.getoutput('pidof x11vnc')
        self._vte.fork_command(cmd)
          
    def connectVNC(self,button):
        self._vte.grab_focus()
        # check if x11vnc is installed
        cmd = '/usr/bin/x11vnc'
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            logging.error('Using x11vnc installed in the system')
        else:
            # check platform
            if platform.machine().startswith('arm'):
                path = os.path.join(activity.get_bundle_path(),
                                    'bin/arm')
            else:
                path = os.path.join(activity.get_bundle_path(),
                                    'bin/i586')
            env = {'LD_LIBRARY_PATH':'%s/lib' % path}
            cmd = os.path.join(path, 'x11vnc')
            logging.error('Using %s', cmd)
        self._vte.fork_command(cmd, envv=env)

    def __key_press_cb(self, window, event):
        return False

class VTE(vte.Terminal):
    def __init__(self):
        vte.Terminal.__init__(self)
        self._configure_vte()
        self.connect("child-exited", lambda term: term.fork_command())

        os.chdir(os.environ["HOME"])
        self.fork_command()

    def _configure_vte(self):
        conf = ConfigParser.ConfigParser()
        conf_file = os.path.join(env.get_profile_path(), 'terminalrc')
        
        if os.path.isfile(conf_file):
            f = open(conf_file, 'r')
            conf.readfp(f)
            f.close()
        else:
            conf.add_section('terminal')

        if conf.has_option('terminal', 'font'):
            font = conf.get('terminal', 'font')
        else:
            font = 'Monospace 8'
            conf.set('terminal', 'font', font)
        self.set_font(pango.FontDescription(font))

        if conf.has_option('terminal', 'fg_color'):
            fg_color = conf.get('terminal', 'fg_color')
        else:
            fg_color = '#000000'
            conf.set('terminal', 'fg_color', fg_color)
        if conf.has_option('terminal', 'bg_color'):
            bg_color = conf.get('terminal', 'bg_color')
        else:
            bg_color = '#FFFFFF'
            conf.set('terminal', 'bg_color', bg_color)
        self.set_colors(gtk.gdk.color_parse (fg_color),
                            gtk.gdk.color_parse (bg_color),
                            [])
                            
        if conf.has_option('terminal', 'cursor_blink'):
            blink = conf.getboolean('terminal', 'cursor_blink')
        else:
            blink = False
            conf.set('terminal', 'cursor_blink', blink)
        
        self.set_cursor_blinks(blink)

        if conf.has_option('terminal', 'bell'):
            bell = conf.getboolean('terminal', 'bell')
        else:
            bell = False
            conf.set('terminal', 'bell', bell)
        self.set_audible_bell(bell)
        
        if conf.has_option('terminal', 'scrollback_lines'):
            scrollback_lines = conf.getint('terminal', 'scrollback_lines')
        else:
            scrollback_lines = 1000
            conf.set('terminal', 'scrollback_lines', scrollback_lines)
            
        self.set_scrollback_lines(scrollback_lines)
        self.set_allow_bold(True)
        
        if conf.has_option('terminal', 'scroll_on_keystroke'):
            scroll_key = conf.getboolean('terminal', 'scroll_on_keystroke')
        else:
            scroll_key = False
            conf.set('terminal', 'scroll_on_keystroke', scroll_key)
        self.set_scroll_on_keystroke(scroll_key)

        if conf.has_option('terminal', 'scroll_on_output'):
            scroll_output = conf.getboolean('terminal', 'scroll_on_output')
        else:
            scroll_output = False
            conf.set('terminal', 'scroll_on_output', scroll_output)
        self.set_scroll_on_output(scroll_output)
        
        if conf.has_option('terminal', 'emulation'):
            emulation = conf.get('terminal', 'emulation')
        else:
            emulation = 'xterm'
            conf.set('terminal', 'emulation', emulation)
        self.set_emulation(emulation)

        if conf.has_option('terminal', 'visible_bell'):
            visible_bell = conf.getboolean('terminal', 'visible_bell')
        else:
            visible_bell = False
            conf.set('terminal', 'visible_bell', visible_bell)
        self.set_visible_bell(visible_bell)
        conf.write(open(conf_file, 'w'))

    def on_gconf_notification(self, client, cnxn_id, entry, what):
        self.reconfigure_vte()

    def on_vte_button_press(self, term, event):
        if event.button == 3:
            self.do_popup(event)
            return True

    def on_vte_popup_menu(self, term):
        pass
