#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2016 Bernd Busse, The MIT License
#

from setuptools import setup


if __name__ == '__main__':
    with open("README.md", 'r') as f:
        readme = f.read()

    setup(name="orangeslices",
          version="0.0.1",
          description="Statusline generator for lemonbar",
          long_description=readme,
          url="http://github.com/tryone144/orangeslices",
          author="Bernd Busse",
          license="MIT",
          packages=["orangeslices"],
          zip_safe=False)
