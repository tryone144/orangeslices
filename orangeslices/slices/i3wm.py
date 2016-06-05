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

RE_WS_TITLE = re.compile('\s*([0-9]*):?\s*(.*)?\s*', re.I)


def i3_connection(callback, on_error):
    try:
        i3 = i3ipc.Connection()

        def restart(i3):
            try:
                i3.get_version()
            except BrokenPipeError:
                print("DO I3 RECONNECT: BROKEN PIPE")
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
            callback(i3, event)

        i3.on('workspace', ws_changed)
        i3.on('ipc-shutdown', restart)

        restart(i3)
    except:
        on_error("Error in I3 communication")


class I3(slice.Slice):
    def __init__(self, strip_title=True, color_fg_focused=slice.COLOR_BLACK,
                 color_bg_focused=slice.COLOR_WHITE, **kwargs):
        super().__init__(**kwargs)

        self.__strip_title = strip_title

        self._color_fg_focused = color_fg_focused
        self._color_bg_focused = color_bg_focused

    def initialize(self, manager):
        super().initialize(manager)

        arguments = {'callback': self._signal,
                     'on_error': self._stop_on_exception}
        self.__conn = Thread(target=i3_connection, name="i3-workspaces",
                             kwargs=arguments, daemon=True)
        self.__conn.start()

    def update(self):
        self.cuts.clear()
        i3 = i3ipc.Connection()
        for ws in i3.get_workspaces():
            self._add_ws(ws.name, ws.num, ws.focused)

        self.propagate()

    def _signal(self, conn, event):
        ws = event.current
        old_ws = event.old

        if event.change == 'focus':
            self._update_ws(ws.name, ws.num, True)
            if old_ws is not None:
                if conn.get_tree().find_by_id(old_ws.id) is not None:
                    self._update_ws(old_ws.name, old_ws.num, False)
        elif event.change == 'init':
            self._add_ws(ws.name, ws.num)
        elif event.change == 'empty':
            self._del_ws(ws.name, ws.num)
        elif event.change == 'urgent':
            self._update_ws(ws.name, ws.num, urgent=ws.urgent)

        self.propagate()

        return True

    def _add_ws(self, name, number, focused=False):
        title = self.__strip_name(name)
        color_fg = self._color_fg_focused if focused else self._color_fg
        color_bg = self._color_bg_focused if focused else self._color_bg

        self._add_cut(name, title, fg=color_fg, bg=color_bg, index=number)

    def _update_ws(self, name, number, focused=False, urgent=False):
        title = self.__strip_name(name)

        if focused:
            color_fg = self._color_fg_focused
            color_bg = self._color_bg_focused
        else:
            color_fg = self._color_fg
            color_bg = self._color_bg

        self._update_cut(number, title, color_fg, color_bg, None, urgent)

    def _del_ws(self, name, number):
        self._del_cut(number)

    def __strip_name(self, name):
        if self.__strip_title:
            match = RE_WS_TITLE.fullmatch(name)
            index = match.group(1)
            title = match.group(2)
            if len(title) == 0:
                title = index if len(index) > 0 else name.strip()
        else:
            title = name.strip()

        return title
