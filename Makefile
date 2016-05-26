#!/usr/bin/env make -f
#
# © 2016 Bernd Busse, The MIT License
#

.PHONY: all build install clean dev

all: build

build:
	./setup.py build

install:
	./setup.py install

clean:
	./setup.py clean

dev:
	./setup.py build
	sudo ./setup.py develop
	@echo "Run Test Example..."
	./examples/default.py
