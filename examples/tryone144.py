#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import orangeslices as osl


def main():
    # Create Orange object
    orange = osl.Orange(lemonbar_args=['-f', 'Source Code Pro for Powerline-9',
                                       '-f', 'Ionicons-12',
                                       '-F', '#FFFFFFFF',
                                       '-B', '#00000000',
                                       '-g', 'x14',
                                       '-a', '40',
                                       '-u', '2'])

    # current date and time
    clock = osl.slices.Clock(timefmt="%a, %d. %b %H:%M",
                             color_fg="#EEE",
                             color_bg="#1793D1",
                             align=osl.ALIGN_RIGHT)

    # i3wm workspace and title
    i3ws = osl.slices.I3ws(strip_title=True,
                           color_fg_focused="#EEE",
                           color_bg_focused="#1793D1",
                           underline_focused=True,
                           color_fg="#888",
                           color_bg="#333",
                           align=osl.ALIGN_LEFT)

    i3title = osl.slices.I3title(maxlen=32,
                                 ellipsis='…',
                                 align=osl.ALIGN_LEFT)

    # Add slices to Orange
    orange.add(clock)
    orange.add(i3ws)
    orange.add(i3title)

    # Start lemonbar and display output of slices
    orange.run()


if __name__ == '__main__':
    main()
