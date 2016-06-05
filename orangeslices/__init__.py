#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse
#

"""Not yet implemented"""
from .orange import Orange, OrangeStyle
from .slice import SliceAlignment, ScreenNumber
from .slices.commands import CommandType
from . import slices

ALIGN_LEFT = SliceAlignment.ALIGN_LEFT
ALIGN_CENTER = SliceAlignment.ALIGN_CENTER
ALIGN_RIGHT = SliceAlignment.ALIGN_RIGHT

SCREEN_FIRST = ScreenNumber.SCREEN_FIRST
SCREEN_SECOND = ScreenNumber.SCREEN_SECOND
SCREEN_THIRD = ScreenNumber.SCREEN_THIRD
SCREEN_FOURTH = ScreenNumber.SCREEN_FOURTH
SCREEN_FIFTH = ScreenNumber.SCREEN_FIFTH
SCREEN_SIXTH = ScreenNumber.SCREEN_SIXTH
SCREEN_SEVENTH = ScreenNumber.SCREEN_SEVENTH
SCREEN_EIGHTH = ScreenNumber.SCREEN_EIGHTH
SCREEN_NINTH = ScreenNumber.SCREEN_NINTH
SCREEN_ALL = ScreenNumber.SCREEN_ALL

STYLE_BLOCKS = OrangeStyle.STYLE_BLOCKS
STYLE_POWERLINE = OrangeStyle.STYLE_POWERLINE

TYPE_ONESHOT = CommandType.TYPE_ONESHOT
TYPE_PERIODIC = CommandType.TYPE_PERIODIC
TYPE_PERSISTENT = CommandType.TYPE_PERSISTENT

__all__ = ['orange', 'slice', 'slices']
