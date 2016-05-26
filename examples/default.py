#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import orangeslices as osl


def main():
    # Create Orange object: handles all slices and runs lemonbar
    orange = osl.Orange()

    # TODO: Set lemonbar options

    # Clock slice: display current time
    clock = osl.slices.Clock(color_fg="#FF02F3DD",
                             align=osl.ALIGN_LEFT)

    # Separator slice: print separator chars
    separator = osl.slices.Separator('|')

    # Command slice: display output of executable
    command = osl.slices.Command(executable="date",
                                 color_bg="#944B",
                                 runtype=osl.TYPE_PERIODIC,
                                 interval=2,
                                 align=osl.ALIGN_CENTER)

    # Add slices to Orange
    orange.add(clock)
    orange.add(separator)
    orange.add(command)

    # Start lemonbar and display output of slices
    orange.run()


if __name__ == '__main__':
    main()
