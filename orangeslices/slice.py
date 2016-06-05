#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from enum import Enum
from gi.repository import GLib
import re
import sys
import traceback


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
    FMT = "%{{F{fg:s}}}%{{B{bg:s}}}%{{U{hl:s}}}{attren:s}{text:s}{attrdis:s}"
    HOOKS = ('text', 'color_fg', 'color_bg', 'color_hl',
             'urgent', 'underline', 'overline')

    def __init__(self, uid, text, color_fg, color_bg, color_hl,
                 urgent, underline, overline):
        super().__init__()
        object.__setattr__(self, 'uid', uid)

        self.text = text
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_hl = color_hl
        self.urgent = urgent
        self.underline = underline
        self.overline = overline

        self.__formatted = text
        self.__needs_refresh = True

    def __setattr__(self, name, value):
        if name == 'uid':
            raise AttributeError("'{}' object attribute 'uid' is read-only"
                                 .format(type(self).__name__))
        if name in CutContainer.HOOKS:
            self.__needs_refresh = True

        super().__setattr__(name, value)

    def formatted(self):
        if self.__needs_refresh:
            if self.urgent:
                fg = COLOR_WHITE
                bg = COLOR_RED
            else:
                fg = self.color_fg
                bg = self.color_bg

            if self.underline or self.overline:
                attren = ''.join(['%{',
                                  '+' if self.underline else '-', 'u}%{',
                                  '+' if self.overline else '-', 'o}'])
                attrdis = "%{-u}%{-o}"
            else:
                attren = ""
                attrdis = ""

            opts = {'text': self.text, 'fg': fg, 'bg': bg, 'hl': self.color_hl,
                    'attren': attren, 'attrdis': attrdis}
            self.__formatted = CutContainer.FMT.format(**opts)
            self.__needs_refresh = False

        return self.__formatted


class Slice(object):
    def __init__(self, color_fg=COLOR_WHITE, color_bg=COLOR_BLACK,
                 color_hl=COLOR_WHITE, align=ALIGN_LEFT,
                 overline=False, underline=False):
        super().__init__()
        self.align = align
        self.cuts = {}

        self._color_fg = SliceColor(color_fg)
        self._color_bg = SliceColor(color_bg)
        self._color_hl = SliceColor(color_hl)
        self._underline = underline
        self._overline = overline

        self._manager = None

    def _add_cut(self, uid, text, fg=None, bg=None, hl=None,
                 urgent=False, under=None, over=None, index=None):
        if index is None:
            index = uid
        if fg is None:
            fg = self._color_fg
        if bg is None:
            bg = self._color_bg
        if hl is None:
            hl = self._color_hl
        if under is None:
            under = self._underline
        if over is None:
            over = self._overline

        text = ' ' + text.strip() + ' '
        cut = CutContainer(uid, text, fg, bg, hl, urgent, under, over)
        self.cuts[index] = cut

    def _get_cut(self, uid):
        return self.cuts[uid]

    def _del_cut(self, uid):
        self.cuts.pop(uid)

    def _update_cut(self, uid, text=None, fg=None, bg=None, hl=None,
                    urgent=None, under=None, over=None):
        cut = self.cuts[uid]
        if text is not None:
            cut.text = ' ' + text.strip() + ' '
        if fg is not None:
            cut.color_fg = fg
        if bg is not None:
            cut.color_bg = bg
        if hl is not None:
            cut.color_hl = hl

        if urgent is not None:
            cut.urgent = urgent
        if under is not None:
            cut.underline = under
        if over is not None:
            cut.overline = over

    def _stop_on_exception(self, message=None):
        if message is not None:
            sys.stderr.write(str(message) + "\n")

        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

        if (self._manager is not None and
                self._manager.is_running):
            self._manager.stop()

    def initialize(self, manager):
        self._manager = manager
        self.update()

    def propagate(self):
        if (self._manager is not None and
                self._manager.is_running):
            self._manager.update()

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
                                                     self._timeout)
        super().initialize(manager)

    def _timeout(self):
        self.update()
        self.propagate()

        return True


class SignaleSlice(Slice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _signal(self, *args, **kwargs):
        self.update()
        self.propagate()

        return True
