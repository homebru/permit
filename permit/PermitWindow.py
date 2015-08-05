# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

# REFERENCE: https://developer.gnome.org/gtk3/stable/ch01s04.html#id-1.2.3.12.5

from locale import gettext as _

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('permit')

from permit_lib import Window

import os
import stat
import grp
import pwd
import re

from gi.repository import GLib # pylint: disable=E0611

# See permit_lib.Window.py for more details about how this class works


class PermitWindow(Window):

    __gtype_name__ = "PermitWindow"

    owner = ''
    group = ''

    octal_owner = 7
    octal_group = 5
    octal_other = 1

    symbolic_owner = 'rwx'
    symbolic_group = 'r-x'
    symbolic_other = '--x'

    symbolic_vals = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx']

    isDir = False

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(PermitWindow, self).finish_initializing(builder)

    """A generator to divide a sequence into chunks of n units."""
    def split_by_n(self, seq, n):
        while seq:
            yield seq[:n]
            seq = seq[n:]

    def refresh_octal(self):
        buff = self.ui.entry_octal.get_buffer()
        buff.set_text(str(PermitWindow.octal_owner) + str(PermitWindow.octal_group) + str(PermitWindow.octal_other), -1)
        # Don't let them chmod 000 on themselves!!!
        if PermitWindow.octal_owner == 0 and PermitWindow.octal_group == 0 and PermitWindow.octal_other == 0:
            self.ui.chmod_button.hide()
        else:
            if self.ui.filechooserbutton1.get_filename():
                self.ui.chmod_button.show()

    def refresh_symbolic(self):
        lead_char = 'd' if PermitWindow.isDir else '-'
        buff = self.ui.entry_symbolic.get_buffer()
        buff.set_text(lead_char + PermitWindow.symbolic_owner + PermitWindow.symbolic_group + PermitWindow.symbolic_other, -1)

    def entry_octal_focus_out_event_cb(self, widget, event):
        self.set_switches()

    def set_switches(self):
        buff = self.ui.entry_octal.get_text()
        while len(buff) < 3:
            buff += '0'
        vals = map(int, buff)
        for x in range(0, 3):
            val = vals[x]
            # if digit is not an octal digit, set it to zero
            # can't do this with int() or oct() because an
            # invalid digit would just raise an error and I
            # would have to handle that error
            val = val if 0 <= val <= 7 else 0
            if x == 0:
                self.ui.switch_owner_read.set_active(val & 4)
                self.ui.switch_owner_write.set_active(val & 2)
                self.ui.switch_owner_execute.set_active(val & 1)

            if x == 1:
                self.ui.switch_group_read.set_active(val & 4)
                self.ui.switch_group_write.set_active(val & 2)
                self.ui.switch_group_execute.set_active(val & 1)

            if x == 2:
                self.ui.switch_other_read.set_active(val & 4)
                self.ui.switch_other_write.set_active(val & 2)
                self.ui.switch_other_execute.set_active(val & 1)

    def entry_symbolic_focus_out_event_cb(self, widget, event):
        reg = re.compile('[-|r|w|x]')
        buff = self.ui.entry_symbolic.get_text()
        txt = buff[1:]
        vals = list(self.split_by_n(txt, 3))
        octal = ''
        for x in range(0, 3):
            str3 = ''
            for y in range(0, 3):
                # if char is not a valid chmod char, set it to dash
                str3 += vals[x][y] if reg.match(vals[x][y]) else '-'
            octal += str(self.symbolic_vals.index(str3))
        self.ui.entry_octal.set_text(octal)
        self.set_switches()

        # I can't figure out the correct way to do the first line of the following
        # code, so I cheated and wrote the entry_octal_focus_out_event_cb code as a
        # sub-function so all that this function and entry_octal_focus_out_event_cb()
        # have to do is call the sub-function!
        # (i.e. circumventing the need to emit an event)
        #
        # event = self.ui.entry_octal.Event(self.ui.entry_octal.FOCUS_CHANGE)
        # event.window = self.ui.entry_octal.get_window()  # the gtk.gdk.Window of the widget
        # event.send_event = True  # this means you sent the event explicitly
        # event.in_ = False  # False for focus out, True for focus in
        # self.ui.entry_octal.emit('focus-out-event', event)

    def filechooserbutton1_file_set_cb(self, widget, data=None):
        self.ui.label_status.set_text("")
        self.get_file_stats(self.ui.filechooserbutton1.get_filename())
        self.ui.chmod_button.show()

    def get_file_stats(self, filepath):
        """
        stat.S_IRWXU
        Mask for file owner permissions.

        stat.S_IRUSR
        Owner has read permission.

        stat.S_IWUSR
        Owner has write permission.

        stat.S_IXUSR
        Owner has execute permission.

        stat.S_IRWXG
        Mask for group permissions.

        stat.S_IRGRP
        Group has read permission.

        stat.S_IWGRP
        Group has write permission.

        stat.S_IXGRP
        Group has execute permission.

        stat.S_IRWXO
        Mask for permissions for others (not in group).

        stat.S_IROTH
        Others have read permission.

        stat.S_IWOTH
        Others have write permission.

        stat.S_IXOTH
        Others have execute permission.
        """

        st = os.stat(filepath)

        PermitWindow.isDir = os.path.isdir(filepath)

        uid = st.st_uid
        gid = st.st_gid

        self.owner = pwd.getpwuid(uid)[0]
        self.group = grp.getgrgid(gid)[0]

        self.ui.entry_owner.set_text(self.owner)
        self.ui.entry_group.set_text(self.group)
        self.ui.box_names.show()

        # Owner
        self.ui.switch_owner_read.set_active(bool(st.st_mode & stat.S_IRUSR))
        self.ui.switch_owner_write.set_active(bool(st.st_mode & stat.S_IWUSR))
        self.ui.switch_owner_execute.set_active(bool(st.st_mode & stat.S_IXUSR))

        # Group
        self.ui.switch_group_read.set_active(bool(st.st_mode & stat.S_IRGRP))
        self.ui.switch_group_write.set_active(bool(st.st_mode & stat.S_IWGRP))
        self.ui.switch_group_execute.set_active(bool(st.st_mode & stat.S_IXGRP))

        # Other
        self.ui.switch_other_read.set_active(bool(st.st_mode & stat.S_IROTH))
        self.ui.switch_other_write.set_active(bool(st.st_mode & stat.S_IWOTH))
        self.ui.switch_other_execute.set_active(bool(st.st_mode & stat.S_IXOTH))

        self.refresh_octal()

    def chmod_button_button_press_event_cb(self, widget, event):
        os.chmod(self.ui.filechooserbutton1.get_filename(), int("0" + self.ui.entry_octal.get_text(), 8))
        self.ui.label_status.set_text("Permissions set to: 0" + self.ui.entry_octal.get_text())
        if self.ui.entry_owner.get_text() != self.owner or self.ui.entry_group.get_text() != self.group:
            os.chown(self.ui.filechooserbutton1.get_filename(), pwd.getpwnam(self.owner).pw_uid, grp.getgrnam(self.group).gr_gid)

    def switch_state_set_cb(self, widget, data=None):
        widget_name = self.builder.get_name(widget)

        types = ['u', 'i', 'e'] # execUte, wrIte, rEad
        char = widget_name[-3:-1][0]
        val = 2 ** types.index(char)

        char = widget_name[8:9]
        if widget.get_state():
            if char == 'w':
                PermitWindow.octal_owner -= val
                PermitWindow.symbolic_owner = PermitWindow.symbolic_vals[PermitWindow.octal_owner]
            elif char == 'r':
                PermitWindow.octal_group -= val
                PermitWindow.symbolic_group = PermitWindow.symbolic_vals[PermitWindow.octal_group]
            else:
                PermitWindow.octal_other -= val
                PermitWindow.symbolic_other = PermitWindow.symbolic_vals[PermitWindow.octal_other]
        else:
            if char == 'w':
                PermitWindow.octal_owner += val
                PermitWindow.symbolic_owner = PermitWindow.symbolic_vals[PermitWindow.octal_owner]
            elif char == 'r':
                PermitWindow.octal_group += val
                PermitWindow.symbolic_group = PermitWindow.symbolic_vals[PermitWindow.octal_group]
            else:
                PermitWindow.octal_other += val
                PermitWindow.symbolic_other = PermitWindow.symbolic_vals[PermitWindow.octal_other]

        self.refresh_octal()
        self.refresh_symbolic()