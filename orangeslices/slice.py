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


class SliceContainer(object):
    def __init__(self, text, color_fg, color_bg, color_hl,
                 align, urgent, underline, overline):
        super().__init__()
        self.text = text
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_hl = color_hl
        self.align = align
        self.urgent = urgent
        self.underline = underline
        self.overline = overline


class Slice(object):
    def __init__(self, color_fg=COLOR_WHITE, color_bg=COLOR_BLACK,
                 color_hl=COLOR_WHITE, align=ALIGN_LEFT,
                 overline=False, underline=False):
        super().__init__()
        self._container = SliceContainer("",
                                         SliceColor(color_fg),
                                         SliceColor(color_bg),
                                         SliceColor(color_hl),
                                         align, False,
                                         underline, overline)
        self.manager = None

    @property
    def text(self):
        return self._container.text

    @property
    def color_fg(self):
        return self._container.color_fg

    @property
    def color_bg(self):
        return self._container.color_bg

    @property
    def color_hl(self):
        return self._container.color_hl

    @property
    def align(self):
        return self._container.align

    @property
    def urgent(self):
        return self._container.urgent

    @property
    def underline(self):
        return self._container.underline

    @property
    def overline(self):
        return self._container.overline

    def _update_text(self, text):
        self._container.text = ' ' + text + ' '

    def update(self):
        raise NotImplementedError("update() needs to be implemented by {}"
                                  .format(self.__class__.__name__))


class IntervalSlice(Slice):
    def __init__(self, interval=5, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(interval, int):
            raise ValueError(
                    "kwargs 'interval' must be of type int not {}"
                    .format(interval.__class__.__name__))

        self.__timeout_id = GLib.timeout_add_seconds(interval, self.timeout)

    def timeout(self):
        self.update()
        if self.manager is not None:
            self.manager.update()

        return True
