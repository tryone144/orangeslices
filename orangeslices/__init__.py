#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse
#

"""Not yet implemented"""
from .orange import Orange, OrangeStyle
from .slice import SliceAlignment
from .slices.commands import CommandType
from . import slices

ALIGN_LEFT = SliceAlignment.ALIGN_LEFT
ALIGN_CENTER = SliceAlignment.ALIGN_CENTER
ALIGN_RIGHT = SliceAlignment.ALIGN_RIGHT

STYLE_BLOCKS = OrangeStyle.STYLE_BLOCKS
STYLE_POWERLINE = OrangeStyle.STYLE_POWERLINE

TYPE_ONE_SHOT = CommandType.TYPE_ONE_SHOT
TYPE_PERIODIC = CommandType.TYPE_PERIODIC
TYPE_PERSISTENT = CommandType.TYPE_PERSISTENT

__all__ = ['orange', 'slice', 'slices']
