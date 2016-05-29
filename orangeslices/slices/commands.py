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
from threading import Thread

from orangeslices import slice


class CommandType(Enum):
    TYPE_ONE_SHOT = 'one_shot'
    TYPE_PERIODIC = 'periodic'
    TYPE_PERSISTENT = 'persistent'

ONE_SHOT = CommandType.TYPE_ONE_SHOT
PERIODIC = CommandType.TYPE_PERIODIC
PERSISTENT = CommandType.TYPE_PERSISTENT


def popen_background(cmd, callback):
    proc = subprocess.Popen(cmd, universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=sys.stderr)

    for line in proc.stdout:
        callback.signal(line)

    proc.terminate()
    try:
        proc.wait(5)
    except subprocess.TimeoutExpired:
        proc.kill()


class Command(slice.Slice):
    def __init__(self, executable, args="", runtype=PERIODIC,
                 maxlen=None, ellipsis='', **kwargs):
        if runtype == PERIODIC:
            if 'interval' not in kwargs:
                raise TypeError(
                        "missing required position argument: 'interval'")

            interval = kwargs.pop('interval')
            if not isinstance(interval, int):
                raise ValueError(
                        "'interval' must be of type int not {}"
                        .format(interval.__class__.__name__))

        super().__init__(**kwargs)

        self.__interval = interval
        self.__maxlen = maxlen
        self.__ellipsis = ellipsis
        self.__runtype = runtype
        self.__cmd = [executable] + shlex.split(args)

        self._add_cut(self.__class__.__name__ + "-" +
                      executable.split('/')[-1], "")

    def initialize(self, manager):
        super().initialize(manager)
        if self.__runtype == PERIODIC:
            self.__timeout_id = GLib.timeout_add_seconds(self.__interval,
                                                         self.timeout)
        elif self.__runtype == PERSISTENT:
            arguments = {'cmd': self.__cmd, 'callback': self}
            self.__first = True
            self.__exec = Thread(target=popen_background,
                                 name="cmd-" + self.__cmd[0].split('/')[-1],
                                 kwargs=arguments, daemon=True)
            self.__exec.start()

    def timeout(self):
        if self.__runtype == PERIODIC:
            self.update()
            if self._manager is not None:
                self._manager.update()

            return True

    def signal(self, line):
        if self.__runtype == PERSISTENT:
            self._update_text(line.rstrip())
            if not self.__first and self._manager is not None:
                self._manager.update()
            self.__first = False

            return True

    def update(self):
        if self.__runtype != PERSISTENT:
            retval = subprocess.run(self.__cmd, check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=sys.stderr,
                                    universal_newlines=True)
            if retval.stdout is not None:
                self._update_text(retval.stdout.rstrip())

    def _update_text(self, text):
        if self.__maxlen and len(text) > self.__maxlen:
            self._update_cut(text[:self.__maxlen].rstrip() +
                             self.__ellipsis)
        else:
            self._update_cut(text)
