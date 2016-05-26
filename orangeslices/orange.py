#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from enum import Enum
from gi.repository import GLib
import sys

from . import slice

AL_LEFT = slice.ALIGN_LEFT
AL_CENTER = slice.ALIGN_CENTER
AL_RIGHT = slice.ALIGN_RIGHT

FMT_COLOR = "%{{F{fg:s} B{bg:s} U{hl:s}}}"


class OrangeStyle(Enum):
    STYLE_BLOCKS = 'blocks'
    STYLE_POWERLINE = 'powerline'

BLOCKS = OrangeStyle.STYLE_BLOCKS
POWERLINE = OrangeStyle.STYLE_POWERLINE


class Orange(object):
    def __init__(self, style=BLOCKS):
        super().__init__()
        self._outs = sys.stdout
        self._errs = sys.stderr

        self._slices = []
        self._timeouts = []

        self.__loop = GLib.MainLoop()
        GLib.threads_init()

    def __render(self, sl):
        pre_attr = ""
        post_attr = ""

        if sl.urgent:
            pre_color = FMT_COLOR.format(fg=slice.COLOR_WHITE,
                                         bg=slice.COLOR_RED,
                                         hl='-')
        else:
            pre_color = FMT_COLOR.format(fg=sl.color_fg,
                                         bg=sl.color_bg,
                                         hl=sl.color_hl)
            if sl.underline:
                pre_attr += "%{+u}"
                post_attr += "%{-u}"
            if sl.overline:
                pre_attr += "%{+o}"
                post_attr += "%{-o}"

        pre = pre_color + pre_attr
        post = post_attr
        return pre + sl.text + post

    def __draw(self):
        output = {AL_LEFT: [],
                  AL_CENTER: [],
                  AL_RIGHT: []}

        for sl in self._slices:
            output[sl.align].append(self.__render(sl))

        left = ''.join(output[AL_LEFT])
        center = ''.join(output[AL_CENTER])
        right = ''.join(output[AL_RIGHT])

        if len(left) > 0:
            self._outs.write("%{l}")
            self._outs.write(left)
        if len(center) > 0:
            self._outs.write("%{c}")
            self._outs.write(center)
        if len(right) > 0:
            self._outs.write("%{r}")
            self._outs.write(right)

        self._outs.write(FMT_COLOR.format(fg='-', bg='-', hl='-'))
        self._outs.write('\n')
        self._outs.flush()

        return True

    def add(self, sl):
        self._slices.append(sl)
        sl.manager = self
        sl.update()

    def update(self):
        self.__draw()

    def run(self):
        self.update()

        try:
            self.__loop.run()
        except KeyboardInterrupt:
            self.__loop.quit()
            self._errs.write("Received SIGINT\n")
            self._errs.flush()

        return
