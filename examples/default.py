#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import orangeslices as osl


def main():
    # Create Orange object: handles all slices and runs lemonbar
    exe = "lemonbar"
    # exe = "/home/bernd/proj/development/lemonbar/lemonbar"
    args = []
    args += ['-f', 'Source Code Pro for Powerline-9', '-f', 'Ionicons-12']
    # args += ['-f', '-*-terminesspowerline-medium-r-normal-*-12-*-*-*-*-*-iso10646-1']
    # args += ['-f', '-*-ionicons-medium-r-normal-*-13-*-*-*-*-*-iso10646-1']
    args += ['-u', '3']
    orange = osl.Orange(lemonbar_exec=exe, lemonbar_args=args)

    # Clock slice: display current time
    clock = osl.slices.Clock(color_fg="#FF02F3DD",
                             align=osl.ALIGN_LEFT)

    # Separator slice: print separator chars
    separator = osl.slices.Separator('|')

    # i3wm slice: display current workspace status
    i3 = osl.slices.I3(strip_title=True)

    # Command slice: display output of executable
    command = osl.slices.Command(executable="date",
                                 color_bg="#944B",
                                 runtype=osl.TYPE_PERIODIC,
                                 interval=2,
                                 align=osl.ALIGN_CENTER,
                                 screen=osl.SCREEN_SECOND,
                                 underline=True)

    # Add slices to Orange
    orange.add(clock)
    orange.add(separator)
    orange.add(i3)
    orange.add(command)

    # Start lemonbar and display output of slices
    orange.run()


if __name__ == '__main__':
    main()
