#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import time

from orangeslices import slice

DEFAULT_DATETIME_FMT = "%H:%M"


class Clock(slice.IntervalSlice):
    def __init__(self, timefmt=DEFAULT_DATETIME_FMT, **kwargs):
        super().__init__(**kwargs)
        self.__timefmt = timefmt

        self._add_cut(0, "")

    def update(self):
        self._update_cut(0, time.strftime(self.__timefmt, time.localtime()))
