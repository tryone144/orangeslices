#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from enum import Enum
from gi.repository import GLib
import re


COLOR_FMT = "#{a:s}{r:s}{g:s}{b:s}"
RE_COLOR_RGB = re.compile("#" + "([0-9A-F])"*3, re.I)
RE_COLOR_ARGB = re.compile("#" + "([0-9A-F])"*4, re.I)
RE_COLOR_RRGGBB = re.compile("#" + "([0-9A-F]{2})"*3, re.I)
RE_COLOR_AARRGGBB = re.compile("#" + "([0-9A-F]{2})"*4, re.I)


def SliceColor(color):
    match = RE_COLOR_RGB.fullmatch(color)
    if match is not None:
        return COLOR_FMT.format(a="FF",
                                r=match.group(1)*2,
                                g=match.group(2)*2,
                                b=match.group(3)*2)

    match = RE_COLOR_ARGB.fullmatch(color)
    if match is not None:
        return COLOR_FMT.format(a=match.group(1)*2,
                                r=match.group(2)*2,
                                g=match.group(3)*2,
                                b=match.group(4)*2)

    match = RE_COLOR_RRGGBB.fullmatch(color)
    if match is not None:
        return COLOR_FMT.format(a="FF",
                                r=match.group(1),
                                g=match.group(2),
                                b=match.group(3))

    match = RE_COLOR_AARRGGBB.fullmatch(color)
    if match is not None:
        return COLOR_FMT.format(a=match.group(1),
                                r=match.group(2),
                                g=match.group(3),
                                b=match.group(4))

    raise ValueError("{:s} is not a valid color format".format(color))


COLOR_WHITE = SliceColor("#FFF")
COLOR_BLACK = SliceColor("#000")
COLOR_RED = SliceColor("#F00")


class SliceAlignment(Enum):
    ALIGN_LEFT = 'l'
    ALIGN_CENTER = 'c'
    ALIGN_RIGHT = 'r'

ALIGN_LEFT = SliceAlignment.ALIGN_LEFT
ALIGN_CENTER = SliceAlignment.ALIGN_CENTER
ALIGN_RIGHT = SliceAlignment.ALIGN_RIGHT


class CutContainer(object):
    def __init__(self, uid, text, order, color_fg, color_bg, color_hl,
                 urgent, underline, overline):
        super().__init__()
        self.text = text
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_hl = color_hl
        self.urgent = urgent
        self.underline = underline
        self.overline = overline

        self.order = order
        self.__uid = uid

    @property
    def uid(self):
        return self.__uid


class Slice(object):
    def __init__(self, color_fg=COLOR_WHITE, color_bg=COLOR_BLACK,
                 color_hl=COLOR_WHITE, align=ALIGN_LEFT,
                 overline=False, underline=False):
        super().__init__()
        self._align = align
        self._color_fg = SliceColor(color_fg)
        self._color_bg = SliceColor(color_bg)
        self._color_hl = SliceColor(color_hl)

        self._cuts = []
        self._manager = None

    @property
    def align(self):
        return self._align

    @property
    def cuts(self):
        return self._cuts

    def _add_cut(self, uid, text, fg=None, bg=None, hl=None,
                 under=False, over=False, order=None, index=None):
        if index is not None and order is not None:
            raise ValueError("only order or index may be specified, not both")

        if order is not None:
            index = 0
            for i, c in enumerate(self._cuts):
                if c.order > order:
                    index = i
                    break
        if index is None:
            index = len(self._cuts)
        if fg is None:
            fg = self._color_fg
        if bg is None:
            bg = self._color_bg
        if hl is None:
            hl = self._color_hl

        text = " " + text.strip() + " "
        cut = CutContainer(uid, text, order, fg, bg, hl, False, under, over)
        self._cuts.insert(index, cut)

    def _get_cut(self, uid):
        for c in self._cuts:
            if c.uid == uid:
                return c

        raise IndexError("cannot find cut with uid '{}'"
                         .format(uid))

    def _del_cut(self, **kwargs):
        if 'uid' in kwargs:
            self._cuts.remove(self._get_cut(kwargs['uid']))
        else:
            index = len(self._cuts) - 1
            if 'index' in kwargs and isinstance(kwargs['index'], int):
                index = kwargs['index']
            self._cuts.pop(index)

    def _update_cut(self, text, **kwargs):
        if 'uid' in kwargs:
            c = self._get_cut(kwargs['uid'])
            c.text = ' ' + text + ' '
        else:
            index = 0
            if 'index' in kwargs and isinstance(kwargs['index'], int):
                index = kwargs['index']
            self._cuts[index].text = ' ' + text + ' '

    def initialize(self, manager):
        self._manager = manager
        self.update()

    def update(self):
        raise NotImplementedError("update() needs to be implemented by {}"
                                  .format(self.__class__.__name__))


class IntervalSlice(Slice):
    def __init__(self, interval=5, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(interval, int):
            raise ValueError(
                    "'interval' must be of type int not {}"
                    .format(interval.__class__.__name__))
        self.__interval = interval

    def initialize(self, manager):
        self.__timeout_id = GLib.timeout_add_seconds(self.__interval,
                                                     self.timeout)
        super().initialize(manager)

    def timeout(self):
        self.update()
        if self._manager is not None:
            self._manager.update()

        return True


class SignaleSlice(Slice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def signal(self, *args, **kwargs):
        self.update()
        if self._manager is not None:
            self._manager.update()

        return True
