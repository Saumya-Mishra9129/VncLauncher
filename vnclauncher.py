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

import sys
import os
import gi
import logging
from gettext import gettext as _
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Vte
from gi.repository import Pango
import dbus

from sugar3.activity import activity
from sugar3 import env
import configparser
import os.path
import struct
import platform
import subprocess
_NM_SERVICE = 'org.freedesktop.NetworkManager'
_NM_IFACE = 'org.freedesktop.NetworkManager'
_NM_PATH = '/org/freedesktop/NetworkManager'
_NM_DEVICE_IFACE = 'org.freedesktop.NetworkManager.Device'


class VncLauncherActivity(activity.Activity):

    def _ipaddr_(self, button):
        self.ipbutton = button
        RetMyIPs = subprocess.check_output(['hostname', '-s', '-I']).decode('utf-8')[:-1]
        myhostname = subprocess.check_output(['hostname']).decode('utf-8')
        total_IPs = RetMyIPs.split()
        IPs = "\n".join(total_IPs)
        if RetMyIPs != "0.0.0.0" and RetMyIPs != "127.0.0.1":
            logging.debug("Found IP Addresses")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="IP Addresses"
            )
            dialog.format_secondary_text(
                 IPs + '\n\n'+
                "Your Hostname is " + myhostname
            )
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                logging.debug("Got IP Addresses")
                self.ipbutton.set_label(
                    'Please Click to find current IP address')
            dialog.destroy()

        else:
            self.ipbutton.set_label(
                'Please Click to find current IP address \n\n' +
                'Error!! check connection'
            )


    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        logging.debug('Starting the X11 VNC activity')

        self.set_title(_('X11 VNC Server Activity'))
        self.connect('key-press-event', self.__key_press_cb)
        args = "Please Click to find current IP address"
        box = Gtk.HBox(False, 10)
        table = Gtk.Table(4, 1, True)
        button = Gtk.Button(args)
        button.connect("clicked", self._ipaddr_)
        table.attach(button, 0, 1, 0, 1,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                     Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, 25, 25)
        button.show()
        button = Gtk.Button("Start X11 VNC Server")
        button.connect("clicked", self.connectVNC)
        table.attach(button, 0, 1, 1, 2,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, 25, 25)
        button.show()

        button = Gtk.Button("Stop X11 VNC Server")
        button.connect("clicked", self.stopVNC)
        table.attach(button, 0, 1, 2, 3, Gtk.AttachOptions.FILL,
                     Gtk.AttachOptions.FILL, 25, 25)
        button.show()

        button = Gtk.Button("Exit VncLauncherActivity")
        button.connect("clicked", lambda w: Gtk.main_quit())
        table.attach(button, 0, 1, 3, 4, Gtk.AttachOptions.FILL,
                     Gtk.AttachOptions.FILL, 25, 25)
        button.show()
        table.show()

        self._vte = VTE()
        self._vte.show()

        self._vte.connect("child-exited", self._quit_cb)
        box.pack_start(self._vte, True, True, 0)
        box.pack_start(table, False, False, 0)

        self.set_canvas(box)
        box.show()
        self._vte.grab_focus()

    def _quit_cb(self, vte, data=None):
        sys.exit(0)

    def stopVNC(self, button):

        cmd = "\x03"  # Ctrl+C
        self._vte.feed_child(cmd.encode('utf-8'))

    def connectVNC(self, button):
        # check if x11vnc is installed
        cmd = '/usr/bin/x11vnc'
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            logging.debug('Using x11vnc installed in the system')
            self._vte.feed_child(cmd.encode('utf-8'))
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="x11vnc is not installed"
            )
            dialog.format_secondary_text(
                "Install x11vnc by clicking on OK"
            )
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                logging.debug("Installing x11vnc")
                if platform.version().find("Ubuntu") > -1 or platform.version().find("Debian") > -1:
                    cmd = "apt install x11vnc"
                if platform.platform().find("Fedora") > -1:
                    cmd = "dnf install x11vnc"
                self._vte.feed_child(cmd.encode('utf-8'))
            dialog.destroy()

    def __key_press_cb(self, window, event):
        return False


class VTE(Vte.Terminal):

    def __init__(self):
        Vte.Terminal.__init__(self)
        self.configure_terminal()
        
        os.chdir(os.environ["HOME"])
        if hasattr(Vte.Terminal, "spawn_sync"):
            self.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                os.environ["HOME"],
                ["/bin/bash"],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None)
        else:
            self.fork_command_full(
                Vte.PtyFlags.DEFAULT,
                os.environ["HOME"],
                ["/bin/bash"],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None)

    def color_parse(self, color):
        rgba = Gdk.RGBA()
        rgba.parse(color)
        return rgba

    def configure_terminal(self):
        conf = configparser.ConfigParser()
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
        self.set_font(Pango.FontDescription(font))

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

        self.set_colors(self.color_parse(bg_color),
                        self.color_parse(fg_color), [])

        if conf.has_option('terminal', 'cursor_blink'):
            blink = conf.getboolean('terminal', 'cursor_blink')
        else:
            blink = 'False'
            conf.set('terminal', 'cursor_blink', blink)
        blink = Vte.CursorBlinkMode(0) if blink == 'False' else Vte.CursorBlinkMode(1)
        self.set_cursor_blink_mode(blink)

        if conf.has_option('terminal', 'bell'):
            bell = conf.getboolean('terminal', 'bell')
        else:
            bell = 'False'
            conf.set('terminal', 'bell', bell)
        self.set_audible_bell(bell)

        if conf.has_option('terminal', 'scrollback_lines'):
            scrollback_lines = conf.getint('terminal', 'scrollback_lines')
        else:
            scrollback_lines = '1000'
            conf.set('terminal', 'scrollback_lines', scrollback_lines)

        self.set_scrollback_lines(int(scrollback_lines))
        self.set_allow_bold(True)

        if conf.has_option('terminal', 'scroll_on_keystroke'):
            scroll_key = conf.getboolean('terminal', 'scroll_on_keystroke')
        else:
            scroll_key = 'False'
            conf.set('terminal', 'scroll_on_keystroke', scroll_key)
        self.set_scroll_on_keystroke(scroll_key)

        if conf.has_option('terminal', 'scroll_on_output'):
            scroll_output = conf.getboolean('terminal', 'scroll_on_output')
        else:
            scroll_output = 'False'
            conf.set('terminal', 'scroll_on_output', scroll_output)
        self.set_scroll_on_output(scroll_output)

        if hasattr(self, 'set_emulation'):
            if conf.has_option('terminal', 'emulation'):
                emulation = conf.get('terminal', 'emulation')
            else:
                emulation = 'xterm'
                conf.set('terminal', 'emulation', emulation)
            self.set_emulation(emulation)

        if hasattr(self, 'set_visible_bell'):
            if conf.has_option('terminal', 'visible_bell'):
                visible_bell = conf.getboolean('terminal', 'visible_bell')
            else:
                visible_bell = 'False'
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
