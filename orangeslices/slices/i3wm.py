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


class i3_connection(Thread):
    def __init__(self, on_error):
        super().__init__(daemon=True)
        self._on_error = on_error
        self._ws_callback = lambda c, e: True
        self._title_callback = lambda c, e: True

        self.conn = None

    def register_workspace_callback(self, callback):
        if callback is not None:
            self._ws_callback = callback
        else:
            self._ws_callback = lambda c, e: True

    def register_title_callback(self, callback):
        if callback is not None:
            self._title_callback = callback
        else:
            self._title_callback = lambda c, e: True

    def __ws_changed(self, conn, event):
        if event.change in ('focus', 'init', 'empty', 'urgent'):
            self._ws_callback(conn, event)
        if event.change == 'focus':
            self._title_callback(conn, event)

    def __title_changed(self, conn, event):
        if event.change in ('focus', 'close', 'move', 'title'):
            self._title_callback(conn, event)

    def restart(self, conn):
        conn.main_quit()

        for _ in range(3):
            try:
                self.conn = i3ipc.Connection()
                break
            except FileNotFoundError:
                sleep(0.5)

        self.conn.on('window', self.__title_changed)
        self.conn.on('workspace', self.__ws_changed)
        self.conn.on('ipc-shutdown', self.restart)

        self.conn.main()

    def run(self):
        try:
            self.conn = i3ipc.Connection()

            self.conn.on('workspace', self.__ws_changed)
            self.conn.on('window', self.__title_changed)
            self.conn.on('ipc-shutdown', self.restart)

            self.conn.main()
        except:
            self._on_error("Error in I3 communication")

__connection__ = None


class I3ws(slice.Slice):
    def __init__(self, strip_title=True, color_fg_focused=slice.COLOR_BLACK,
                 color_bg_focused=slice.COLOR_WHITE, **kwargs):
        super().__init__(**kwargs)

        self.__strip_title = strip_title

        self._color_fg_focused = color_fg_focused
        self._color_bg_focused = color_bg_focused

        self.__outputs = self.__get_outputs()

    def initialize(self, manager):
        super().initialize(manager)
        global __connection__

        if __connection__ is None:
            __connection__ = i3_connection(self._stop_on_exception)
            __connection__.start()

        __connection__.register_workspace_callback(self._signal)

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


class I3title(slice.Slice):
    def __init__(self, maxlen=None, ellipsis='', **kwargs):
        super().__init__(**kwargs)

        self.__maxlen = maxlen
        self.__ellipsis = ellipsis

    def initialize(self, manager):
        super().initialize(manager)
        global __connection__

        if __connection__ is None:
            __connection__ = i3_connection(self._stop_on_exception)
            __connection__.start()

        __connection__.register_title_callback(self._signal)

    def update(self):
        self.cuts.clear()
        i3 = i3ipc.Connection()
        name = i3.get_tree().find_focused().name
        if self.__maxlen and len(name) > self.__maxlen:
            self._add_cut(0, name[:self.__maxlen].rstrip() +
                          self.__ellipsis)
        else:
            self._add_cut(0, name)

        self.propagate()

    def _signal(self, conn, event):
        empty = False
        win = None
        try:
            win = event.container
        except AttributeError:
            empty = (len(event.current.descendents()) == 0)

        if event.change == 'focus':
            if empty:
                self.__update_title("")
            elif win is not None:
                self.__update_title(win.name)
        elif event.change == 'title':
            if win.focused:
                self.__update_title(win.name)

        self.propagate()

        return True

    def __update_title(self, text):
        if self.__maxlen and len(text) > self.__maxlen:
            self._update_cut(0, text[:self.__maxlen].rstrip() +
                             self.__ellipsis)
        else:
            self._update_cut(0, text)
