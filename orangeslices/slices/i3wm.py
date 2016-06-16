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

        self.__outputs = self.__get_outputs()

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
            number, _ = self.__strip_name(ws.name)
            self._add_ws(ws.name, index=number, focused=ws.focused,
                         output=self.__outputs[ws.output])

        self.propagate()

    def _signal(self, conn, event):
        ws = event.current
        old_ws = event.old

        if event.change == 'focus':
            self._update_ws(ws.name, focused=True)
            if old_ws is not None:
                if conn.get_tree().find_by_id(old_ws.id) is not None:
                    self._update_ws(old_ws.name, focused=False)
        elif event.change == 'init':
            self._add_ws(ws.name, output=self.__get_output(conn, ws.name))
        elif event.change == 'empty':
            self._del_ws(ws.name)
        elif event.change == 'move':
            self._update_ws(ws.name, output=self.__get_output(conn, ws.name))
        elif event.change == 'urgent':
            self._update_ws(ws.name, urgent=ws.urgent)

        self.propagate()

        return True

    def _add_ws(self, name, index=None, output=None, focused=False):
        number, title = self.__strip_name(name)
        color_fg = self._color_fg_focused if focused else self._color_fg
        color_bg = self._color_bg_focused if focused else self._color_bg

        if index is not None:
            number = index

        self._add_cut(name, title, fg=color_fg, bg=color_bg, index=number,
                      screen=output)

    def _update_ws(self, name, index=None, focused=False, urgent=False,
                   output=None):
        number, title = self.__strip_name(name)

        if focused:
            color_fg = self._color_fg_focused
            color_bg = self._color_bg_focused
        else:
            color_fg = self._color_fg
            color_bg = self._color_bg

        if index is not None:
            number = index

        self._update_cut(number, title, color_fg, color_bg, None, urgent,
                         screen=output)

    def _del_ws(self, name, index=None):
        if index is not None:
            number = index
        else:
            number, _ = self.__strip_name(name)

        self._del_cut(number)

    def __strip_name(self, name):
        if self.__strip_title:
            match = RE_WS_TITLE.fullmatch(name)
            index = match.group(1)
            title = match.group(2)
            if len(title) == 0:
                title = index if len(index) > 0 else name.strip()
            index = int(index)
        else:
            index = name.strip()
            title = name.strip()

        return index, title

    def __get_output(self, conn, name):
        for ws in conn.get_workspaces():
            if ws.name == name:
                return self.__outputs[ws.output]

        return slice.SCREEN_ALL

    def __get_outputs(self):
        def position(output):
            return output.rect.y, output.rect.x

        outputs = {}
        i3 = i3ipc.Connection()

        for i, output in enumerate(sorted(
                filter(lambda o: o.active, i3.get_outputs()), key=position)):
            outputs[output.name] = slice.ScreenNumber.from_index(i)

        return outputs
