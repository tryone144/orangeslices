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

COLOR_RESET = "%{F-}%{B-}%{U-}"
ATTR_RESET = "%{-u}%{-o}"

FMT_COLOR_FG = "%{{F{:s}}}"
FMT_COLOR_BG = "%{{B{:s}}}"
FMT_COLOR_HL = "%{{U{:s}}}"

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
        self.is_running = False

        if isinstance(lemonbar_args, str):
            lemonbar_args = shlex.split(lemonbar_args)
        self.__bar_cmd = [lemonbar_exec] + lemonbar_args
        self.__outstream = sys.stdout

        self.__started = False
        self.__bar_exec = None

        self.__loop = GLib.MainLoop()
        GLib.threads_init()

    def __render(self, sl):
        slice_output = ""
        first_cut = True

        for _, cut in sorted(sl.cuts.items()):
            if not first_cut:
                slice_output += "%{F#FFFFFFFF}%{B#FF000000}|"
            else:
                first_cut = False

            slice_output += cut.formatted()

        return slice_output

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

        self.__write(COLOR_RESET + ATTR_RESET)
        self.__write('\n')
        self.__outstream.flush()

        return True

    def __write(self, string):
        self.__outstream.write(string)
        sys.stdout.write(string)

    def add(self, sl):
        """add slice to output"""
        self._slices.append(sl)
        sl.initialize(self)

    def update(self):
        if (self.__bar_exec is not None and
                self.__bar_exec.poll() is not None):
            sys.stderr.write("lemonbar terminated, quitting...\n")
            sys.stderr.flush()
            self.__loop.quit()
            return

        self.__draw()

    def run(self):
        """start lemonbar and generate statusline"""
        if self.__started:
            raise RuntimeError("Orange already started.")

        # start lemonbar
        # TODO: handle lemonbar click actions
        self.__started = True
        self.__bar_exec = subprocess.Popen(self.__bar_cmd,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.DEVNULL,
                                           stderr=sys.stderr,
                                           universal_newlines=True)

        self.__outstream = self.__bar_exec.stdin
        self.is_running = True
        self.update()

        # start event loop
        try:
            self.__loop.run()
        except KeyboardInterrupt:
            self.__loop.quit()
            sys.stderr.write("Received SIGINT, quitting...\n")
            sys.stderr.flush()

        self.__cleanup()

    def stop(self):
        self.__loop.quit()
        self.__cleanup()

    def __cleanup(self):
        if self.__started and self.is_running:
            # stop lemonbar
            self.__bar_exec.terminate()
            try:
                self.__bar_exec.wait(10)
            except subprocess.TimeoutExpired:
                self.__bar_exec.kill()
