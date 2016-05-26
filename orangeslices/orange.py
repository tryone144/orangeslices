#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from enum import Enum
from gi.repository import GLib
import shlex
import subprocess
import sys

from . import slice

AL_LEFT = slice.ALIGN_LEFT
AL_CENTER = slice.ALIGN_CENTER
AL_RIGHT = slice.ALIGN_RIGHT

FMT_COLOR = "%{{F{fg:s} B{bg:s} U{hl:s}}}"

LEMONBAR_EXEC = "/usr/bin/lemonbar"
LEMONBAR_ARGS = ""


class OrangeStyle(Enum):
    STYLE_BLOCKS = 'blocks'
    STYLE_POWERLINE = 'powerline'

BLOCKS = OrangeStyle.STYLE_BLOCKS
POWERLINE = OrangeStyle.STYLE_POWERLINE


class Orange(object):
    def __init__(self, style=BLOCKS, lemonbar_exec=LEMONBAR_EXEC,
                 lemonbar_args=LEMONBAR_ARGS):
        super().__init__()
        self._slices = []

        self.__bar_cmd = [lemonbar_exec] + shlex.split(lemonbar_args)
        self.__bar_exec = None
        self.__outstream = sys.stdout

        self.__started = False
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
            self.__write("%{l}")
            self.__write(left)
        if len(center) > 0:
            self.__write("%{c}")
            self.__write(center)
        if len(right) > 0:
            self.__write("%{r}")
            self.__write(right)

        self.__write(FMT_COLOR.format(fg='-', bg='-', hl='-'))
        self.__write('\n')
        self.__outstream.flush()

        return True

    def __write(self, string):
        self.__outstream.write(string.encode('utf-8'))

    def add(self, sl):
        self._slices.append(sl)
        sl.manager = self
        sl.update()

    def update(self):
        if self.__bar_exec.poll() is not None:
            sys.stderr.write("lemonbar terminated, quitting...\n")
            sys.stderr.flush()
            self.__loop.quit()
            return

        self.__draw()

    def run(self):
        if self.__started:
            raise RuntimeError("Orange already started.")

        self.__started = True
        self.__bar_exec = subprocess.Popen(self.__bar_cmd,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.DEVNULL,
                                           stderr=sys.stderr)

        self.__outstream = self.__bar_exec.stdin
        self.update()

        try:
            self.__loop.run()
        except KeyboardInterrupt:
            self.__loop.quit()
            sys.stderr.write("Received SIGINT, quitting...\n")
            sys.stderr.flush()

        self.__bar_exec.terminate()
        try:
            self.__bar_exec.wait(10)
        except subprocess.TimeoutExpired:
            self.__bar_exec.kill()

        return
