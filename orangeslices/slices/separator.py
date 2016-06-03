#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from orangeslices import slice


class Separator(slice.Slice):
    def __init__(self, char=' ', width=1, **kwargs):
        super().__init__(**kwargs)
        self._add_cut(0, "")
        self.cuts[0].text = char * width

    def update(self):
        pass
