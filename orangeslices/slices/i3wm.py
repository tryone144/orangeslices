#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import i3ipc
import re
from threading import Thread
from time import sleep

from orangeslices import slice

RE_WS_TITLE = re.compile('^\s*([0-9]*)(:)?\s*(.*)?\s*$', re.I)


def i3_connection(callback):
    i3 = i3ipc.Connection()

    def restart(i3):
        try:
            i3.get_version()
        except BrokenPipeError:
            i3 = i3ipc.Connection()

        count = 0
        while count < 3:
            count += 1
            try:
                i3.main()
                return
            except FileNotFoundError:
                sleep(0.5)

        raise RuntimeError("cannot (re)connect to i3 ipc socket")

    def ws_changed(i3, event):
        callback.signal(event)

    i3.on('ipc-shutdown', restart)
    i3.on('workspace', ws_changed)

    restart(i3)


class I3(slice.Slice):
    def __init__(self, strip_title=True, color_fg_focused=slice.COLOR_BLACK,
                 color_bg_focused=slice.COLOR_WHITE, **kwargs):
        super().__init__(**kwargs)

        self.strip = strip_title

        self._color_fg_focused = color_fg_focused
        self._color_bg_focused = color_bg_focused

    def initialize(self, manager):
        super().initialize(manager)
        self.__conn = Thread(target=i3_connection, name="i3-workspaces",
                             kwargs={'callback': self}, daemon=True)
        self.__conn.start()

    def signal(self, event):
        ws = event.current
        old_ws = event.old
        if event.change == 'focus':
            self._update_ws(ws.name, True)
            if old_ws is not None:
                self._update_ws(old_ws.name, False)
        elif event.change == 'init':
            self._add_ws(ws.name, ws.num)
        elif event.change == 'empty':
            self._del_ws(ws.name)
        elif event.change == 'urgent':
            self._update_ws(ws.name, urgent=ws.urgent)

        if self._manager is not None:
            self._manager.update()

        return True

    def update(self):
        self._cuts.clear()
        i3 = i3ipc.Connection()
        for ws in i3.get_workspaces():
            self._add_ws(ws.name, ws.num, ws.focused)

    def _add_ws(self, name, order, focused=False):
        _, title = self.__strip_name(name)
        color_fg = self._color_fg_focused if focused else self._color_fg
        color_bg = self._color_bg_focused if focused else self._color_bg

        self._add_cut(name, title, fg=color_fg, bg=color_bg, order=order)

    def _update_ws(self, name, focused=False, urgent=False):
        _, title = self.__strip_name(name)

        c = self._get_cut(uid=name)
        if urgent:
            c.color_fg = slice.COLOR_WHITE
            c.color_bg = slice.COLOR_RED
        elif focused:
            c.color_fg = self._color_fg_focused
            c.color_bg = self._color_bg_focused
        else:
            c.color_fg = self._color_fg
            c.color_bg = self._color_bg

        self._update_cut(title, uid=name)

    def _del_ws(self, name):
        self._del_cut(uid=name)

    def __strip_name(self, name):
        match = RE_WS_TITLE.match(name)
        index = match.group(1)
        if self.strip:
            title = match.group(3)
        else:
            title = name.strip()

        try:
            index = int(index)
        except:
            index = None

        if title == "":
            title = str(index)

        return index, title
