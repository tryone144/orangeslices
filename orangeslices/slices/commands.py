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
import select
from threading import Thread
from collections import deque

from orangeslices import slice


class CommandType(Enum):
    TYPE_ONESHOT = 'oneshot'
    TYPE_PERIODIC = 'periodic'
    TYPE_PERSISTENT = 'persistent'

ONESHOT = CommandType.TYPE_ONESHOT
PERIODIC = CommandType.TYPE_PERIODIC
PERSISTENT = CommandType.TYPE_PERSISTENT


def popen_background(cmd, callback, on_error):
    try:
        proc_stderr = deque([], 15)
        proc = subprocess.Popen(cmd, shell=True,
                                universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        events = select.POLLIN | select.POLLPRI | select.POLLHUP
        fn_stdout = proc.stdout.fileno()
        fn_stderr = proc.stderr.fileno()

        poll = select.poll()
        poll.register(proc.stdout, events)
        poll.register(proc.stderr, events)

        while proc.poll() is None:
            result = poll.poll()
            for fd, event in result:
                if event & select.POLLHUP and proc.poll() is None:
                    try:
                        _, stderr = proc.communicate(timeout=5)
                        proc_stderr.append(stderr.rstrip())
                    except subprocess.TimeoutExpired:
                        proc.kill()
                else:
                    if fd == fn_stdout:
                        callback(proc.stdout.readline().rstrip())
                    elif fd == fn_stderr:
                        proc_stderr.append(proc.stderr.readline().rstrip())

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, ' '.join(cmd),
                                                stderr='\n'.join(proc_stderr))

        print("DONE")
    except:
        on_error("Backgroundprocess '" + ' '.join(cmd) + "' failed.")


class Command(slice.Slice):
    def __init__(self, executable, args="", runtype=PERIODIC,
                 maxlen=None, ellipsis='', **kwargs):
        if runtype == PERIODIC:
            if 'interval' not in kwargs:
                raise TypeError(
                        "missing required position argument: 'interval'")

            self.__interval = kwargs.pop('interval')
            if not isinstance(self.__interval, int):
                raise ValueError(
                        "'interval' must be of type int not {}"
                        .format(type(self.__interval).__name__))

        super().__init__(**kwargs)

        self.__maxlen = maxlen
        self.__ellipsis = ellipsis

        self.__runtype = runtype
        self.__cmd = [executable] + shlex.split(args)

        self._add_cut(type(self).__name__ + "-" + executable.split('/')[-1],
                      text="", index=0)

    def initialize(self, manager):
        super().initialize(manager)

        if self.__runtype == PERIODIC:
            self.__timeout_id = GLib.timeout_add_seconds(self.__interval,
                                                         self._timeout)
        elif self.__runtype == PERSISTENT:
            arguments = {'cmd': self.__cmd,
                         'callback': self._signal,
                         'on_error': self._stop_on_exception}
            self.__exec = Thread(target=popen_background,
                                 name="cmd-" + self.__cmd[0].split('/')[-1],
                                 kwargs=arguments, daemon=True)
            self.__exec.start()

    def update(self):
        if self.__runtype != PERSISTENT:
            retval = subprocess.run(self.__cmd, check=True, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=sys.stderr,
                                    universal_newlines=True)
            if retval.stdout is not None:
                self.__update_text(retval.stdout.rstrip())

    def _signal(self, line):
        if self.__runtype == PERSISTENT:
            self.__update_text(line.rstrip())
            self.propagate()

            return True

    def _timeout(self):
        if self.__runtype == PERIODIC:
            self.update()
            self.propagate()

            return True

    def __update_text(self, text):
        if self.__maxlen and len(text) > self.__maxlen:
            self._update_cut(0, text[:self.__maxlen].rstrip() +
                             self.__ellipsis)
        else:
            self._update_cut(0, text)
