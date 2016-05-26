#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

import orangeslices as osl


def main():
    orange = osl.Orange()

    sep1 = osl.slices.Separator()
    sep2 = osl.slices.Separator('|')
    clock = osl.slices.Clock(color_fg="#FF02F3DD", align=osl.ALIGN_LEFT)
    orange.add(sep1)
    orange.add(clock)
    orange.add(sep2)

    orange.run()


if __name__ == '__main__':
    main()
